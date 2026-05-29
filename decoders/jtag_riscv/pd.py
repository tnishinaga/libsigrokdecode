##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2026 Toshifumi Nishinaga <tnishinaga.dev@gmail.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd
from .dtm_regs import *

rv_jtag_ir:dict[str,str] = {
    '00000': 'BYPASS',
    '00001': 'IDCODE',
    '10000': 'DTMCS',
    '10001': 'DMI',
}
    

class Decoder(srd.Decoder):
    api_version:int = 3
    id:str = 'jtag_riscv'
    name:str = 'JTAG / RISC-V'
    longname:str = 'JTAG / RISC-V'
    desc:str = 'RISC-V JTAG protocol'
    license:str = 'gplv2+'
    inputs:list[str] = ['jtag']
    outputs = []
    tags:list[str] = ['Debug/trace']
    # current IR register value
    current_ir:str = 'IDCODE'
    # default abits is 7bit
    abits: int = 7
    annotations = (
        ('dmi_send', 'DMI Send'),
        ('dtmcs_send', 'DtmCs Send'),
        ('dmi_receive', 'DMI Receive'),
        ('dtmcs_receive', 'DtmCs Receive'),
        ('warning', 'Warning'),
    )
    annotation_rows = (
        ('send', 'Send', (0,1)),
        ('receive', 'Receive', (2,3)),
        ('warnings', 'Warnings', (4,)),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'IDLE'

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def decode(self, ss, es, data):
        cmd:str = data[0]
        val = data[1]
        if cmd == 'IR TDI':
            ir_bit:str = data[1][0]
            self.current_ir = rv_jtag_ir.get(ir_bit, "Unknown")
            return
        if not(cmd.startswith("DR")):
            return
        
        try:
            binary:int = int(val[0],2)
        except:
            return

        # DR 
        is_input: bool = "TDO" in cmd
        is_output: bool = "TDI" in cmd
        is_dtmcs: bool = self.current_ir == "DTMCS"
        is_dmi: bool = self.current_ir == "DMI"

        index: int | None = None
        tap_reg: str | None = None
        data: str | None = None
        if is_dtmcs:
            tap_reg = "DTMCS"
            dtmcs:DtmCs = DtmCs.parse_int(binary)
            if is_input and self.abits != dtmcs.abits:
                print(f'change abits from {self.abits} to {dtmcs.abits}')
                self.abits = dtmcs.abits
            data = str(dtmcs)
            if is_input:
                index = 3
            if is_output:
                index = 1
        if is_dmi:
            tap_reg = "DMI"
            dmi:Dmi = Dmi.parse_int(is_output, self.abits, binary)
            data = str(dmi)
            if is_input:
                index = 2
            if is_output:
                index = 0
        if index is not None and tap_reg is not None and data is not None:
            self.put(ss, es, self.out_ann, [index,[f'{tap_reg} {"send" if is_output else "recv"}: {data}']])


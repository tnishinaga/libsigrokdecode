import math
from enum import Enum, IntEnum

class DtmCs:
    def __init__(self, version: int, abits: int, dmistat: int, idle: int, dmireset: int, dmihardreset: int):
        self.version = version
        self.abits = abits
        self.dmistat = dmistat
        self.idle = idle
        self.dmireset = dmireset
        self.dmihardreset = dmihardreset

    @staticmethod
    def parse_int(dtm_binary: int) -> DtmCs | None:
        if dtm_binary != 0 and 32 <= math.log2(dtm_binary):
            print("dtm_binary too large")
            return None
        version = dtm_binary & 0b1111
        abits = (dtm_binary >> 4) & 0b111111
        dmistat = (dtm_binary >> 10) & 0b11
        idle = (dtm_binary >> 12) & 0b111
        dmireset = (dtm_binary >> 16) & 0b1
        dmihardreset = (dtm_binary >> 17) & 0b1
        return DtmCs(version, abits, dmistat, idle, dmireset, dmihardreset)

    def __str__(self) -> str:
        version_desc: list[str] = ['0.11', '0.13']
        version = version_desc[self.version] if self.version < len(version_desc) else 'Unknown'
        dmistat_desc: list[str] = ['NoError', 'Reserved', 'OpFailed', 'Progress']
        dmistat = dmistat_desc[self.dmistat]
        return f'version:{version}, dmistat:{dmistat}, idle: {str(self.idle)}, dmireset: {str(self.dmireset)}, dmihardreset: {str(self.dmihardreset)}'


class DmiOpSend(IntEnum):
    Unk0 = 0
    Read = 1
    Write = 2
    Unk3 = 3
    def __str__(self) -> str:
        if self.name.startswith('Unk'):
            return f"{self.value:#04x}"
        return self.name
            


class DmiOpReceive(IntEnum):
    PreviousSuccess = 0
    Unk1 = 1
    PreviousFailed = 2
    Busy = 3
    def __str__(self) -> str:
        if self.name.startswith('Unk'):
            return f"{self.value:#04x}"
        return self.name

class Dmi():
    def __init__(self, send:bool, abits: int, address:int, data: int, op: int):
        self.send:bool = send
        self.abits:int = abits
        self.address:int = address
        self.data:int = data
        self.op:int = op

    @staticmethod
    def parse_int(send:bool, abits: int, dmi_binary:int) -> Dmi | None:
        op:int = dmi_binary & 0b11
        data:int = (dmi_binary >> 2) & 0xffff_ffff
        address:int = (dmi_binary >> (32 + 2)) & ((1 << abits) - 1)
        return Dmi(send, abits, address, data, op)

    def __str__(self) -> str:
        if self.send:
            op = str(DmiOpSend(self.op))
        else:
            op = str(DmiOpReceive(self.op))
        try:
            address = str(DmRegAddress(self.address))
        except ValueError:
            address = "Unknown"
        return 'address:{}({:#04x}), data:{:#010x}, op: {}'.format(address, self.address, self.data, op)

class DmRegAddress(IntEnum):
    data0 = 0x04
    data1 = 0x05
    data2 = 0x06
    data3 = 0x07
    data4 = 0x08
    data5 = 0x09
    data6 = 0x0a
    data7 = 0x0b
    data8 = 0x0c
    data9 = 0x0d
    data10 = 0x0e
    data11 = 0x0f
    dmcontrol = 0x10
    dmstatus = 0x11
    hartinfo = 0x12
    haltsum1 = 0x13
    hawindowsel = 0x14
    hawindow = 0x15
    abstractcs = 0x16
    command = 0x17
    abstractauto = 0x18
    confstrptr0 = 0x19
    confstrptr1 = 0x1a
    confstrptr2 = 0x1b
    confstrptr3 = 0x1c
    nextdm = 0x1d
    progbuf0 = 0x20
    progbuf1 = 0x21
    progbuf2 = 0x22
    progbuf3 = 0x23
    progbuf4 = 0x24
    progbuf5 = 0x25
    progbuf6 = 0x26
    progbuf7 = 0x27
    progbuf8 = 0x28
    progbuf9 = 0x29
    progbuf10 = 0x2a
    progbuf15 = 0x2f
    authdata = 0x30
    haltsum2 = 0x34
    haltsum3 = 0x35
    sbaddress3 = 0x37
    sbcs = 0x38
    sbaddress0 = 0x39
    sbaddress1 = 0x3a
    sbaddress2 = 0x3b
    sbdata0 = 0x3c
    sbdata1 = 0x3d
    sbdata2 = 0x3e
    sbdata3 = 0x3f
    haltsum0 = 0x40

    def __str__(self) -> str:
        return self.name





        

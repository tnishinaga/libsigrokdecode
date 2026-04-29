import math
from enum import Enum, IntEnum


class DtmCs:
    def __init__(
        self,
        version: int,
        abits: int,
        dmistat: int,
        idle: int,
        dmireset: int,
        dmihardreset: int,
    ):
        self.version = version
        self.abits = abits
        self.dmistat = dmistat
        self.idle = idle
        self.dmireset = dmireset
        self.dmihardreset = dmihardreset

    @staticmethod
    def parse_int(dtm_binary: int) -> DtmCs | None:  # noqa: F821
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
        version_desc: list[str] = ["0.11", "0.13"]
        version = (
            version_desc[self.version]
            if self.version < len(version_desc)
            else "Unknown"
        )
        dmistat_desc: list[str] = ["NoError", "Reserved", "OpFailed", "Progress"]
        dmistat = dmistat_desc[self.dmistat]
        return f"version:{version}, dmistat:{dmistat}, idle: {str(self.idle)}, dmireset: {str(self.dmireset)}, dmihardreset: {str(self.dmihardreset)}"


class DmiOpSend(IntEnum):
    Nop = 0
    Read = 1
    Write = 2
    Unk3 = 3

    def __str__(self) -> str:
        if self.name.startswith("Unk"):
            return f"{self.value:#04x}"
        return self.name


class DmiOpReceive(IntEnum):
    PreviousSuccess = 0
    Unk1 = 1
    PreviousFailed = 2
    Busy = 3

    def __str__(self) -> str:
        if self.name.startswith("Unk"):
            return f"{self.value:#04x}"
        return self.name


class Dmi:
    def __init__(self, send: bool, abits: int, address: int, data: int, op: int):
        self.send: bool = send
        self.abits: int = abits
        self.address: int = address
        self.data: int = data
        self.op: int = op

    @staticmethod
    def parse_int(send: bool, abits: int, dmi_binary: int) -> Dmi | None:  # noqa: F821
        op: int = dmi_binary & 0b11
        data: int = (dmi_binary >> 2) & 0xFFFF_FFFF
        address: int = (dmi_binary >> (32 + 2)) & ((1 << abits) - 1)
        return Dmi(send, abits, address, data, op)

    def __str__(self) -> str:
        if self.send:
            op = str(DmiOpSend(self.op))
        else:
            op = str(DmiOpReceive(self.op))
        try:
            address = DmRegAddress(self.address)
            match address:
                case DmRegAddress.dmstatus:
                    data = str(DmStatus(self.data))
                case DmRegAddress.dmcontrol:
                    data = str(DmControl(self.data))
                case _:
                    data = f"{self.data:#010x}"
                    pass
            address = str(address)
        except ValueError:
            return f"address:{self.address:#04x}, data:{self.data:#010x}, op: {op}"
        tmp_op = DmiOpSend(self.op)
        if self.send and (tmp_op == DmiOpSend.Read or tmp_op == DmiOpSend.Nop):
            # send 0 when Read request
            # data don't care
            return f"address: {address}, op: {op}"

        return f"{data}, op: {op}"


class DmRegAddress(IntEnum):
    data0 = 0x04
    data1 = 0x05
    data2 = 0x06
    data3 = 0x07
    data4 = 0x08
    data5 = 0x09
    data6 = 0x0A
    data7 = 0x0B
    data8 = 0x0C
    data9 = 0x0D
    data10 = 0x0E
    data11 = 0x0F
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
    confstrptr1 = 0x1A
    confstrptr2 = 0x1B
    confstrptr3 = 0x1C
    nextdm = 0x1D
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
    progbuf10 = 0x2A
    progbuf15 = 0x2F
    authdata = 0x30
    haltsum2 = 0x34
    haltsum3 = 0x35
    sbaddress3 = 0x37
    sbcs = 0x38
    sbaddress0 = 0x39
    sbaddress1 = 0x3A
    sbaddress2 = 0x3B
    sbdata0 = 0x3C
    sbdata1 = 0x3D
    sbdata2 = 0x3E
    sbdata3 = 0x3F
    haltsum0 = 0x40

    def __str__(self) -> str:
        return self.name


class DmStatus:
    simple_flags: dict[str, int] = {}
    data: int = 0

    def __init__(self, data: int):
        self.simple_flags["implicit_ebreak"] = (data >> 22) & 1
        self.simple_flags["all_have_reset"] = (data >> 19) & 1
        self.simple_flags["any_have_reset"] = (data >> 18) & 1
        self.simple_flags["all_resume_ack"] = (data >> 17) & 1
        self.simple_flags["any_resume_ack"] = (data >> 16) & 1
        self.simple_flags["all_non_exisent"] = (data >> 15) & 1
        self.simple_flags["any_non_exisent"] = (data >> 14) & 1
        self.simple_flags["all_unavail"] = (data >> 13) & 1
        self.simple_flags["any_unavail"] = (data >> 12) & 1
        self.simple_flags["all_running"] = (data >> 11) & 1
        self.simple_flags["any_running"] = (data >> 10) & 1
        self.simple_flags["all_halted"] = (data >> 9) & 1
        self.simple_flags["any_halted"] = (data >> 8) & 1
        self.simple_flags["all_halted"] = (data >> 9) & 1
        self.simple_flags["any_halted"] = (data >> 8) & 1
        self.simple_flags["authenticated"] = (data >> 7) & 1
        self.simple_flags["authbusy"] = (data >> 6) & 1
        self.simple_flags["has_reset_halt_req"] = (data >> 5) & 1
        self.simple_flags["confstrptr_valid"] = (data >> 4) & 1
        self.version = data & 0b1111
        self.data = data

    def __str__(self) -> str:
        if self.version == 0:
            return "no DM present"
        buf = f"DmStatus({DmRegAddress.dmstatus:#04x}) {{"
        for field in filter(lambda x: x[1] == 1, self.simple_flags.items()):
            buf += f"{field[0]}(1), "
        match self.version:
            case 1:
                buf += "v0.11"
            case 2:
                buf += "v0.13"
            case 15:
                buf += "not conform"
            case _:
                buf += "Unknown version"
        buf += f"}}({self.data:#010x})"
        return buf


class DmControl:
    simple_flags: dict[str, int] = {}
    hartsel: int = 0
    hasel: int = 0
    data: int = 0

    def __init__(self, data: int):
        self.simple_flags["halt_req"] = (data >> 31) & 1
        self.simple_flags["resume_req"] = (data >> 30) & 1
        self.simple_flags["hart_reset"] = (data >> 29) & 1
        self.simple_flags["ack_have_reset"] = (data >> 28) & 1
        self.hasel = (data >> 26) & 1
        hartsel_lo = (data >> 16) & 0b1111111111  # 10bit
        hartsel_hi = (data >> 6) & 0b1111111111  # 10bit
        self.hartsel = hartsel_hi << 10 | hartsel_lo
        self.simple_flags["set_reset_halt_req"] = (data >> 3) & 1
        self.simple_flags["clr_reset_halt_req"] = (data >> 2) & 1
        self.simple_flags["ndm_reset"] = (data >> 1) & 1
        self.simple_flags["dmactive"] = (data >> 0) & 1
        self.data = data

    def __str__(self) -> str:
        buf = f"DmControl({DmRegAddress.dmcontrol:#04x}) {{"
        for field in filter(lambda x: x[1] == 1, self.simple_flags.items()):
            buf += f"{field[0]}(1), "
        buf += "hasel: {}({}), ".format(
            "single" if self.hasel == 0 else "multi", self.hasel
        )
        if self.hartsel == 0:
            buf += "hartsel: 0"
        else:
            buf += f"hartsel: {self.hartsel:#022b}"
        buf += f"}}({self.data:#010x})"
        return buf


class HartInfo:
    n_scratch: int = 0
    data_access: bool = False
    data_size: int = 0
    data_addr: int = 0
    data: int = 0

    def __init__(self, data: int):
        self.n_scratch = (data >> 20) & 0b1111  # 4bits
        self.data_access = True if (data >> 16) & 1 == 1 else { False}
        self.data_size = (data >> 12) & 0b1111  # 4bits
        self.data_addr = (data >> 0) & 0xFFF  # 12bits
        self.data = data

    def __str__(self) -> str:
        if self.data == 0:
            return f"HartInfo({DmRegAddress.hartinfo:#04x}) {{0(may be not present)}}"

        buf = f"HartInfo({DmRegAddress.hartinfo:#04x}) {{"
        buf += f"nscratch: {self.n_scratch}, "
        buf += "data_access: {}({})".format("CSR" if self.data_access else {"mmap"}, self.data_access)
        buf += f"data_size: {self.data_size}, "
        buf += f"data_addr: {self.data_addr}, "
        buf += f"}}({self.data:#010x})"
        return buf

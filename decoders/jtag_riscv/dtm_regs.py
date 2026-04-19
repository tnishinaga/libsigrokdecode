import math
from enum import Enum

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


class DmiOpSend(Enum):
    Unk0 = 0
    Read = 1
    Write = 2
    Unk3 = 3
    def __str__(self) -> str:
        match self:
            case DmiOpSend.Read:
                return "Read"
            case DmiOpSend.Write:
                return "Write"
            case _:
                return f"{self.value:#04x}"
            


class DmiOpReceive(Enum):
    PreviousSuccess = 0
    Unk1 = 1
    PreviousFailed = 2
    Unk3 = 3
    def __str__(self) -> str:
        match self:
            case DmiOpReceive.PreviousSuccess:
                return "PreviousSuccess"
            case DmiOpReceive.PreviousFailed:
                return "PreviousFailed"
            case _:
                return f"{self.value:#04x}"

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
        return 'address:{:#04x}, data:{:#010x}, op: {}'.format(self.address, self.data, op)

# class DmControl(Dmi):



        

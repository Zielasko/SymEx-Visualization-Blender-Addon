from enum import Enum

class Opcode(Enum):
    LUI = 1
    AUIPC = 2
    JAL = 3
    JALR = 4
    BEQ = 5
    BNE = 6
    BLT = 7
    BGE = 8
    BLTU = 9
    BGEU = 10
    LB = 11
    LH = 12
    LW = 13
    LBU = 14
    LHU = 15
    SB = 16
    SH = 17
    SW = 18
    ADDI = 19
    SLTI = 20
    SLTIU = 21
    XORI = 22
    ORI = 23
    ANDI = 24
    SLLI = 25
    SRLI = 26
    SRAI = 27
    ADD = 28
    SUB = 29
    SLL = 30
    SLT = 31
    SLTU = 32
    XOR = 33
    SRL = 34
    SRA = 35
    OR = 36
    AND = 37
    MRET = 38
    FENCE = 39
    FENCE_I = 40
    ECALL = 41
    EBREAK = 42
    CSRRW = 43
    CSRRS = 44
    CSRRC = 45
    CSRRWI = 46
    CSRRSI = 47
    CSRRCI = 48
    MUL = 49
    MULH = 50
    MULHSU = 51
    MULHU = 52
    DIV = 53
    DIVU = 54
    REM = 55
    REMU = 56
    MULW = 57
    DIVW = 58
    DIVUW = 59
    REMW = 60
    REMUW = 61
    C_LWSP = 62
    C_LDSP = 63
    C_FLWSP = 64
    C_FLDSP = 65
    C_SWSP = 66
    C_FSWSP = 67
    C_FSDSP = 68
    C_LW = 69
    C_FLW = 70
    C_FLD = 71
    C_SW = 72
    C_FSW = 73
    C_FSD = 74
    C_J = 75
    C_JAL = 76
    C_JR = 77
    C_JALR = 78
    C_BEQZ = 79
    C_BNEZ = 80
    C_LI = 81
    C_LUI = 82
    C_ADDI = 83
    C_ADDI16SP = 84
    C_ADDI4SPN = 85
    C_SLLI = 86
    C_SRLI = 87
    C_SRAI = 88
    C_ANDI = 89
    C_MV = 90
    C_ADD = 91
    C_AND = 92
    C_OR = 93
    C_XOR = 94
    C_SUB = 95
    C_ADDW = 96
    C_SUBW = 97
    C_ILLEGAL = 98
    C_NOP = 99
    C_EBREAK = 100
    LR_W = 101
    LR_D = 102
    SC_W = 103
    SC_D = 104
    AMOSWAP_W = 105
    AMOSWAP_D = 106
    AMOADD_W = 107
    AMOADD_D = 108
    AMOAND_W = 109
    AMOAND_D = 110
    AMOOR_W = 111
    AMOOR_D = 112
    AMOXOR_W = 113
    AMOXOR_D = 114
    AMOMAX_W = 115
    AMOMAX_D = 116
    AMOMIN_W = 117
    AMOMIN_D = 118
    AMOMAXU_W = 119
    AMOMAXU_D = 120
    AMOMINU_W = 121
    AMOMINU_D = 122
    FLW = 123
    FSW = 124
    FADD_S = 125
    FSUB_S = 126
    FMUL_S = 127
    FDIV_S = 128
    FSQRT_S = 129
    FMIN_S = 130
    FMAX_S = 131
    FMADD_S = 132
    FMSUB_S = 133
    FNMSUB_S = 134
    FNMADD_S = 135
    FCVT_W_S = 136
    FCVT_L_S = 137
    FCVT_S_W = 138
    FCVT_S_L = 139
    FCVT_WU_S = 140
    FCVT_LU_S = 141
    FCVT_S_WU = 142
    FCVT_S_LU = 143
    FSGNJ_S = 144
    FSGNJN_S = 145
    FSGNJX_S = 146
    FMV_X_W = 147
    FMV_W_X = 148
    FEQ_S = 149
    FLT_S = 150
    FLE_S = 151
    FCLASS_S = 152
    FLD = 153
    FSD = 154
    FADD_D = 155
    FSUB_D = 156
    FMUL_D = 157
    FDIV_D = 158
    FSQRT_D = 159
    FMIN_D = 160
    FMAX_D = 161
    FMADD_D = 162
    FMSUB_D = 163
    FNMSUB_D = 164
    FNMADD_D = 165
    FCVT_W_D = 166
    FCVT_L_D = 167
    FCVT_D_W = 168
    FCVT_D_L = 169
    FCVT_WU_D = 170
    FCVT_LU_D = 171
    FCVT_D_WU = 172
    FCVT_D_LU = 173
    FCVT_S_D = 174
    FCVT_D_S = 175
    FSGNJ_D = 176
    FSGNJN_D = 177
    FSGNJX_D = 178
    FMV_X_D = 179
    FMV_D_X = 180
    FEQ_D = 181
    FLT_D = 182
    FLE_D = 183
    FCLASS_D = 184
    ERROR = 999

class Opcode_type(Enum):
    none = 0
    ECALL = 1
    Arith = 2
    Jump = 3
    Branch = 4
    Load = 5
    Store = 6
    CSR = 7

class Reg(Enum):
    none = -1
    zero = 0
    ra = 1
    sp = 2
    gp = 3
    tp = 4
    t0 = 5  
    t1 = 6  
    t2 = 7  
    s0 = 8
    s1 = 9
    a0 = 10 
    a1 = 11 
    a2 = 12 
    a3 = 13 
    a4 = 14 
    a5 = 15 
    a6 = 16 
    a7 = 17 
    s2 = 18
    s3 = 19
    s4 = 20
    s5 = 21
    s6 = 22
    s7 = 23
    s8 = 24
    s9 = 25
    s10 = 26
    s11 = 27
    t3 = 28 
    t4 = 29 
    t5 = 30 
    t6 = 31 

"""
1 create, 0 keep, -1 destroy, 2 destroy old symbolic value in rd and overwrite with new that does not derive from previous rd
"""
class Symbolic_Beh(Enum):
    none = 0 #all registers concrete
    update = 1 #blue
    create = 2 #green
    overwrite = 3 #overwrite with unrelated symbolic value #orange
    destroy = 4 #red
    special = 5 #white
    unknown = 999 # Error while analysing symbolic behavior
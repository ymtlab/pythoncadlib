from enum import Enum, IntEnum


class MyIntEnum(IntEnum):
    @classmethod
    def get_value(cls, value):
        try:
            return cls(value)
        except ValueError:
            return value


class CadTypes:
    class AsmPlane:

        class Base(MyIntEnum):
            Top   = 1
            Front = 2
            Right = 3

        class Status(MyIntEnum):
            Visible   = 1
            Invisible = 2
            Notextist = 3

    class Color(MyIntEnum):
        NONE         = 0
        White        = 1
        Red          = 2
        Green        = 3
        Yellow       = 4
        Blue         = 5
        Magenta      = 6
        Cyan         = 7
        Gray         = 8
        Orange       = 9
        LightGreen   = 10
        YellowishGeen= 11
        SkyBlue      = 12
        Purple       = 13
        BlueGreen    = 14
        Fresh        = 15
        PaleOrange   = 15
        Black        = 16
        Extra1       = 17
        Extra2       = 18
        Extra3       = 19
        Extra4       = 20
        Extra5       = 21
        Extra6       = 22
        Extra7       = 23
        Extra8       = 24
        Extra9       = 25
        Extra10      = 26
        Extra11      = 27
        Extra12      = 28
        Extra13      = 29
        Extra14      = 30
        Extra15      = 31

    class CgMode(MyIntEnum):
        NONE = 0
        Shade = 1
        Edge = 2
        Hidden = 3

    class Entity:

        class Symbol(MyIntEnum):
            FINAL = 1
            MID1 = 2
            MID2 = 50
            MID3 = 51
            CENTER_FIX = 3
            CENTER_TAIL = 4
            CENTER_SPR = 5
            METAL = 6
            NAIL_ZIP = 7
            MIKIRI = 8
            INDICATOR = 9
            S = 10
            S1 = 11
            S2 = 12
            S3 = 13
            S4 = 14
            S5 = 15
            S6 = 16
            S7 = 17
            S8 = 18
            S9 = 19
            S10 = 20
            S11 = 21
            S12 = 22
            S13 = 23
            S14 = 24
            S15 = 25
            S16 = 26
            S17 = 27
            S18 = 28
            S19 = 29
            R = 30
            R1 = 31
            R2 = 32
            R3 = 33
            R4 = 34
            R5 = 35
            R6 = 36
            R7 = 37
            R8 = 38
            R9 = 39
            R10 = 40
            R11 = 41
            R12 = 42
            R13 = 43
            R14 = 44
            R15 = 45
            R16 = 46
            R17 = 47
            R18 = 48
            R19 = 49
        
        class FinishMark(MyIntEnum):
            Mark1 = 1
            Mark2 = 2
            Mark3 = 3
            Mark4 = 4
            Mark5 = 5
     
        class Hatch(MyIntEnum):
            PATTERN_01 = 1
            PATTERN_02 = 2
            PATTERN_03 = 3
            PATTERN_04 = 4
            PATTERN_05 = 5
            PATTERN_06 = 6
            PATTERN_07 = 7
            PATTERN_08 = 8
            PATTERN_EX = 9
        
        class SMark:
            class RemoveType(MyIntEnum):
                NOREMOVE = 0
                REMOVE = 1
                NODEL = 2

            class LaySymbol(MyIntEnum):
                NONE = 0
                PAR = 1
                VER = 2
                X = 3
                M = 4
                C = 5
                R = 6
                N = 7
                P = 8

            class Format(MyIntEnum):
                JIS_B0031_1994 = 0
                JIS_B0031_2003 = 1
 
        class Datum:
            class ReflineType(MyIntEnum):
                NONE = 0
                Line = 1
                Circle = 2
                Arc = 3
                Point = 4
        
        class AdditionalLine(MyIntEnum):
            LEFT  = 1
            RIGHT = 2
            BOTH  = 3

        class Arrow(MyIntEnum):
            LEFT  = 1
            RIGHT = 2
            BOTH  = 3

        class Blend(MyIntEnum):
            BALL    = 1
            CHAMFER = 2

        class Boolean(MyIntEnum):
            UNITE     = 1
            SUBTRACT  = 2
            INTERSECT = 3

        class DimensionWord(MyIntEnum):
            WORD  = 4
            WORD1 = 1
            WORD2 = 2
            WORD3 = 3

        class MoveDimension(MyIntEnum):
            ANY = 1
            HOR = 2
            VER = 3

        class CutPlane(MyIntEnum):
            XY  = 1
            YZ  = 2
            ZX  = 3
            ANY = 4

        class Shell(MyIntEnum):
            INNER = 1
            OUTER = 2
            BOTH  = 3

        class SplineKind(MyIntEnum):
            NORMAL   = 1
            PERIODIC = 2
            FIXED    = 3

        class Text:
            class ARRANGE(MyIntEnum):
                AUTO   = 1
                CENT   = 2
                LEFT   = 3
                RIGHT  = 4
                TOP    = 5
                BOTTOM = 6

            class Base(MyIntEnum):
                LeftTop      = 1
                CenterTop    = 2
                RightTop     = 3
                LeftCenter   = 4
                CenterCenter = 5
                RightCenter  = 6
                LeftBottom   = 7
                CenterBottom = 8
                RightBottom  = 9

        class Trim(MyIntEnum):
            ALL  = 0
            ONE  = 1
            TWO  = 2
            NONE = 3
            THIN = 4
            
        class Kind(MyIntEnum):
            Segment = 0
            RPart   = 1
            Group   = 2
            Refer   = 3
            Part    = 6
            Invalid = 100
 
        class Type(MyIntEnum):
            NONE       = 0   # 
            POINT      = 1   # 点
            LINE       = 2   # 線
            ARC        = 5   # 円弧
            CIR        = 6   # 円
            FIL        = 7   # ?
            OLD_ELP    = 9   # ?
            OLD_ELPA   = 10  # ?
            CURV       = 11  # ?
            OTHER_DRAW = 12  # その他作図要素
            RECT       = 13  # ?
            SYM        = 14  # シンボル／矢視／切断線
            APL        = 15  # 角／長円／角穴／座標寸法線
            SPL        = 16  # スプライン
            TEXT       = 21  # 文字列
            LBL        = 22  # 注記
            CENL       = 23  # 中心線
            ARL        = 24  # 円弧長寸法線
            DLIN       = 25  # 長さ寸法線
            DANG       = 26  # 角度寸法線
            DARC       = 27  # 径寸法線
            FMRK       = 28  # 仕上記号
            DCHA       = 29  # 面取り寸法線
            BALL       = 34  # 風船
            DELTA      = 37  # デルタ
            OTHER_DIM  = 42  # その他寸法線
            WELD       = 43  # 溶接記号
            LEAD       = 44  # 矢印
            GTOL       = 45  # 幾何公差
            SMRK       = 46  # 表面粗さ
            PCON       = 63  # 正多角錐／正多角錐台
            PRSM       = 64  # 多角錐／多角錐台
            LPRJ       = 65  # 偏心投影体
            EPRJ       = 66  # 拡張投影体
            ROT        = 67  # 回転体
            CONE       = 68  # 円錐／円錐台
            PCYL       = 70  # 正多角柱
            CYL        = 71  # 円柱
            SPHR       = 72  # 球／部分球
            CAP        = 73  # キャップ
            TORUS      = 74  # トーラス
            BOX        = 75  # 直方体
            PRJT       = 76  # 投影体
            PARAM3D    = 77  # ?
            SOLID      = 85  # ソリッド
            FCSOLID    = 87  # F.C.ソリッド
            ELP        = 88  # 楕円
            ELPA       = 89  # 楕円弧
            MARK       = 90  # 記号
            HATCH      = 92  # ハッチング
            HATCH_EX   = 94  # 拡張ハッチング
            DXLN       = 98  # ?
            RPART      = 201 # 実像部品
            PART       = 204 # パート
            EXTRA_INFO = 207 # ?
            MKUP       = 211 # マークアップ
            MKUP_DLIN  = 217 # マークアップ（長さ寸法）
            MKUP_DARC  = 218 # マークアップ（径寸法）
            MKUP_DANG  = 219 # マークアップ（角度寸法）
            MKUP_LBL   = 220 # マークアップ（注記）
            CIRSYM     = 224 # ?
            MOTLIN     = 230 # ?
            INTLKLIN   = 231 # ?
            MOTSYM     = 232 # ?
            DIAGSTR    = 234 # ?
            WIRING     = 240 # ?

        class BodyType(MyIntEnum):
            Other = 0
            Solid = 1
            Sheet = 2
            Wire  = 3
        
        class FcState(MyIntEnum):
            NONE        = 0
            Normal      = 1
            Element     = 2
            NonManifold = 3

        def get_type(self, _type: int):
            if _type in CadTypes.Entity.Type._value2member_map_:
                return CadTypes.Entity.Type(_type)
            return _type

        def body_types(self):
            return [
                CadTypes.Entity.Type.BOX,
                CadTypes.Entity.Type.CAP,
                CadTypes.Entity.Type.CONE,
                CadTypes.Entity.Type.CYL,
                CadTypes.Entity.Type.EPRJ,
                CadTypes.Entity.Type.FCSOLID,
                CadTypes.Entity.Type.LPRJ,
                CadTypes.Entity.Type.PCON,
                CadTypes.Entity.Type.PCYL,
                CadTypes.Entity.Type.PRJT,
                CadTypes.Entity.Type.PRSM,
                CadTypes.Entity.Type.ROT,
                CadTypes.Entity.Type.SOLID,
                CadTypes.Entity.Type.SPHR,
                CadTypes.Entity.Type.TORUS
            ]

        def dimension_types(self):
            return [
                CadTypes.Entity.Type.APL,       # 角／長円／角穴／座標寸法線
                CadTypes.Entity.Type.ARL,       # 円弧長寸法線
                CadTypes.Entity.Type.BALL,      # 風船
                CadTypes.Entity.Type.DANG,      # 角度寸法線
                CadTypes.Entity.Type.DARC,      # 径寸法線
                CadTypes.Entity.Type.DCHA,      # 面取り寸法線
                CadTypes.Entity.Type.DELTA,     # デルタ
                CadTypes.Entity.Type.DLIN,      # 長さ寸法線
                CadTypes.Entity.Type.FMRK,      # 仕上記号
                CadTypes.Entity.Type.GTOL,      # 幾何公差
                CadTypes.Entity.Type.LBL,       # 注記
                CadTypes.Entity.Type.LEAD,      # 矢印
                CadTypes.Entity.Type.MARK,      # 記号
                CadTypes.Entity.Type.MKUP,      # マークアップ
                CadTypes.Entity.Type.MKUP_DANG, # マークアップ（角度寸法）
                CadTypes.Entity.Type.MKUP_DARC, # マークアップ（径寸法）
                CadTypes.Entity.Type.MKUP_DLIN, # マークアップ（長さ寸法）
                CadTypes.Entity.Type.MKUP_LBL,  # マークアップ（注記）
                CadTypes.Entity.Type.OTHER_DIM, # その他寸法線
                CadTypes.Entity.Type.SMRK,      # 表面粗さ
                CadTypes.Entity.Type.SYM        # シンボル／矢視／切断線`
            ]

        def geometry_include_types(self):
            return [
                CadTypes.Entity.Type.POINT,
                CadTypes.Entity.Type.LINE,
                CadTypes.Entity.Type.ARC,
                CadTypes.Entity.Type.CIR,
                CadTypes.Entity.Type.SYM,
                CadTypes.Entity.Type.APL,
                CadTypes.Entity.Type.SPL,
                CadTypes.Entity.Type.TEXT,
                CadTypes.Entity.Type.LBL,
                CadTypes.Entity.Type.ARL,
                CadTypes.Entity.Type.DLIN,
                CadTypes.Entity.Type.DANG,
                CadTypes.Entity.Type.DARC,
                CadTypes.Entity.Type.FMRK,
                CadTypes.Entity.Type.DCHA,
                CadTypes.Entity.Type.BALL,
                CadTypes.Entity.Type.DELTA,
                CadTypes.Entity.Type.OTHER_DIM,
                CadTypes.Entity.Type.WELD,
                CadTypes.Entity.Type.LEAD,
                CadTypes.Entity.Type.GTOL,
                CadTypes.Entity.Type.SMRK,
                CadTypes.Entity.Type.ELP,
                CadTypes.Entity.Type.ELPA,
                CadTypes.Entity.Type.MARK,
                CadTypes.Entity.Type.HATCH,
                CadTypes.Entity.Type.HATCH_EX,
                CadTypes.Entity.Type.MKUP_LBL
            ]
        
        def entity_types(self):
            return [
                CadTypes.Entity.Type.POINT      ,  # 点
                CadTypes.Entity.Type.LINE       ,  # 線
                CadTypes.Entity.Type.ARC        ,  # 円弧
                CadTypes.Entity.Type.CIR        ,  # 円
                CadTypes.Entity.Type.FIL        ,  # 
                CadTypes.Entity.Type.OLD_ELP    ,  # 
                CadTypes.Entity.Type.OLD_ELPA   ,  # 
                CadTypes.Entity.Type.CURV       ,  # 
                CadTypes.Entity.Type.OTHER_DRAW ,  # その他作図要素
                CadTypes.Entity.Type.RECT       ,  # 
                CadTypes.Entity.Type.SYM        ,  # シンボル／矢視／切断線
                CadTypes.Entity.Type.APL        ,  # 角／長円／角穴／座標寸法線
                CadTypes.Entity.Type.SPL        ,  # スプライン
                CadTypes.Entity.Type.TEXT       ,  # 文字列
                CadTypes.Entity.Type.LBL        ,  # 注記
                CadTypes.Entity.Type.CENL       ,  # 中心線
                CadTypes.Entity.Type.ARL        ,  # 円弧長寸法線
                CadTypes.Entity.Type.DLIN       ,  # 長さ寸法線
                CadTypes.Entity.Type.DANG       ,  # 角度寸法線
                CadTypes.Entity.Type.DARC       ,  # 径寸法線
                CadTypes.Entity.Type.FMRK       ,  # 仕上記号
                CadTypes.Entity.Type.DCHA       ,  # 面取り寸法線
                CadTypes.Entity.Type.BALL       ,  # 風船
                CadTypes.Entity.Type.DELTA      ,  # デルタ
                CadTypes.Entity.Type.OTHER_DIM  ,  # その他寸法線
                CadTypes.Entity.Type.WELD       ,  # 溶接記号
                CadTypes.Entity.Type.LEAD       ,  # 矢印
                CadTypes.Entity.Type.GTOL       ,  # 幾何公差
                CadTypes.Entity.Type.SMRK       ,  # 表面粗さ
                CadTypes.Entity.Type.PCON       ,  # 正多角錐／正多角錐台
                CadTypes.Entity.Type.PRSM       ,  # 多角錐／多角錐台
                CadTypes.Entity.Type.LPRJ       ,  # 偏心投影体
                CadTypes.Entity.Type.EPRJ       ,  # 拡張投影体
                CadTypes.Entity.Type.ROT        ,  # 回転体
                CadTypes.Entity.Type.CONE       ,  # 円錐／円錐台
                CadTypes.Entity.Type.PCYL       ,  # 正多角柱
                CadTypes.Entity.Type.CYL        ,  # 円柱
                CadTypes.Entity.Type.SPHR       ,  # 球／部分球
                CadTypes.Entity.Type.CAP        ,  # キャップ
                CadTypes.Entity.Type.TORUS      ,  # トーラス
                CadTypes.Entity.Type.BOX        ,  # 直方体
                CadTypes.Entity.Type.PRJT       ,  # 投影体
                CadTypes.Entity.Type.SOLID      ,  # ソリッド
                CadTypes.Entity.Type.FCSOLID    ,  # F.C.ソリッド
                CadTypes.Entity.Type.ELP        ,  # 楕円
                CadTypes.Entity.Type.ELPA       ,  # 楕円弧
                CadTypes.Entity.Type.MARK       ,  # 記号
                CadTypes.Entity.Type.HATCH      ,  # ハッチング
                CadTypes.Entity.Type.HATCH_EX   ,  # 拡張ハッチング
                CadTypes.Entity.Type.DXLN       ,  # 
                CadTypes.Entity.Type.MKUP       , # マークアップ
                CadTypes.Entity.Type.MKUP_DLIN  , # マークアップ（長さ寸法）
                CadTypes.Entity.Type.MKUP_DARC  , # マークアップ（径寸法）
                CadTypes.Entity.Type.MKUP_DANG  , # マークアップ（角度寸法）
                CadTypes.Entity.Type.MKUP_LBL     # マークアップ（注記）
            ]

    class Geometry:
        class Type(MyIntEnum):
            POINT2D       = 1
            LINE2D        = 2
            CIRCLE2D      = 4
            ARC2D         = 5
            ELLIPSE2D     = 7
            ELPARC2D      = 8
            SPLINE2D      = 16
            POINT3D       = 64
            LINE3D        = 65
            CIRCLE3D      = 67
            ARC3D         = 68
            BSPLINE3D     = 69
            OTHER_CURVE   = 255
            PLANE         = 305
            CYLINDER      = 306
            CONE          = 307
            TORUS         = 308
            SWEPT         = 309
            SPUN          = 310
            SPHERE        = 311
            BSURF         = 312
            CAP           = 313
            OTHER_SURF    = 511
            SYMBOL        = 526
            APL           = 527
            NOTE          = 533
            LBL           = 534
            CENL          = 535
            ARL           = 536
            DLIN          = 537
            DANG          = 538
            DARC          = 539
            FMRK          = 540
            DCHA          = 541
            BALL          = 546
            DELTA         = 549
            OTHER_DRAFT   = 554
            WELD          = 555
            LEAD          = 556
            GTOL          = 557
            SMRK          = 558
            MARK          = 602
            HATCH         = 604
            SYM_METAL     = 626
            SYM_INDICATOR = 627
            ARROW_VIEW    = 628
            CUTLINE       = 629
            SIMWELD       = 655
            TOLDATUM      = 657
            OTHER_GEOM    = 767

        class DimensionValue:
            class Mark2(MyIntEnum):
                NONE = 0
                SMK = 1
                QMK = 2

            class Mark3(MyIntEnum):
                NONE = 0
                FAIMK = 1
                SQMK = 2
                RMK = 3
                CMK = 4
                TMK = 5
                MMK = 6
                ARCMK = 7
                CRMK = 8
                OPT = 9

            class Tolerance(MyIntEnum):
                NONE = 0
                ONE = 1
                TWO = 2
            
        class DimensionLine:
            
            class ROUND(MyIntEnum):
                UP = 1
                DOWN = 2
                OF = 3

            class AngleType(MyIntEnum):
                DEGREE0 = 1 # 度
                MINUTE0 = 2 # 度分
                SECOND0 = 3 # 度分秒
                DEGREE = 5 # 度
                MINUTE = 6 # 度分
                SECOND = 7 # 度分秒

            class DisplayAngle(MyIntEnum):
                ALONG = 1
                HORIZON = 3

            class Arrow(MyIntEnum):
                NONE = 0
                ONE = 1
                BOTH = 2
                DOT = 3

            class TermMark(MyIntEnum):
                NONE = 0
                DISP = 1
                HIDE = 2

            class AidLine(MyIntEnum):
                NONE = 0
                DISP = 1
                HIDE = 2

            class TolerancePosition(MyIntEnum):
                TOP = 1
                CENTER = 2
                BOTTOM = 3

    class Mass:
        class Unit(MyIntEnum):
            MM_G  = 1
            MM_KG = 2
            CM_G  = 3
            CM_KG = 4
            M_G   = 5
            M_KG  = 6
            
        class Accuracy(MyIntEnum):
            High = 1
            Middle = 2
            Low = 3

    class WF:
        class Type(MyIntEnum):
            WORK   = 0
            GLOBAL = 1

    class VS:
        class Type(MyIntEnum):
            WORK_VS     = 0
            GLOBAL_VIEW = 1
            VIEW        = 2
            LOCAL_VIEW  = 3

        class View(MyIntEnum):
            ISOME  = -999
            LOCAL  = -1
            GLOBAL = 0
            TOP    = 1
            FRONT  = 2
            RIGHT  = 3
            LEFT   = 4
            BACK   = 5
            BOTTOM = 6

    class Line:
        class Width(MyIntEnum):
            NONE   = 0 # 
            BOLD   = 1 # 太線
            MIDDLE = 2 # 中線
            THIN   = 3 # 細線

        class Style(MyIntEnum):
            NONE          = 0 # 
            SOLID         = 1 # 実線
            DASH          = 2 # 破線
            ONE_DOT_CHAIN = 3 # 一点鎖線
            TWO_DOT_CHAIN = 4 # 二点鎖線
            DOT           = 5 # 点線
            LONG_DASH     = 6 # 長破線

    class Select:
        class Mode(MyIntEnum):
            Entity = 0
            Part = 1
            Multi = 2

        class MultiInit(MyIntEnum):
            Segment = 0
            Part = 1
            NONE = 2

        class Status(MyIntEnum):
            Go = 0
            Entity = 1
            Edge = 2
            Face = 3
            Point = 4

        class PointStatus(MyIntEnum):
            Any = 0
            Entity = 1
            Edge = 2
            Face = 3
            Int = 4

    class Search:
        class EntityType(MyIntEnum):
            All = 0
            Draw = 1
            Draft = 2
            Solid = 3

    class Welding:
        class Simple(MyIntEnum):
            Mark1 = 1
            Mark2 = 2
            Mark3 = 3
            Mark4 = 4
            Mark5 = 5
            Mark6 = 6
            Mark7 = 7
            Mark8 = 8
            
        class Place(MyIntEnum):
            Upper     = 1
            Under     = 2
            BothSides = 3

        class Mark(MyIntEnum):
            I             = 1  # Ｉ形 
            V             = 2  # Ｖ形 
            U             = 3  # Ｕ形 
            レ            = 4  # レ形 
            J             = 5  # Ｊ形 
            Vflare        = 6  # フレアＶ形 
            Suminiku      = 7  # すみ肉 
            Chidori       = 8  # 千鳥 
            ChidoriEvenly = 9  # 等間隔千鳥 
            Plug          = 10 # プラグ 
            Bead          = 11 # ビ－ト 
            Spot          = 12 # 点
            Projection    = 13 # プロジェクション 
            Seam          = 14 # シ－ム 
            X             = 15 # 付合せ
            レflare       = 16 # フレアレ形 
            Nikumori      = 17 # 肉盛り 
            ArcSeam       = 18 # アークシーム 
            ArcSpot       = 19 # アークスポット 
            Spot1         = 20 # スポット１ 
            Spot2         = 21 # スポット２ 
            Seam2         = 22 # シーム２ 
            Frange        = 23 # フランジ 
            FrangeOneside = 24 # 片フランジ 
            Plug2         = 25 # プラグ２ 
            XPart         = 34 # 部分溶込み片面斜角突合せ溶接 
            VPart         = 35 # 部分溶込み片面Ｖ形突合せ溶接 
            ChidoriSpot   = 36 # 千鳥スポット溶接 
            Sim           = 37 # シム溶接 
            VStayPlunk    = 38 # ステープランク片面Ｖ形突合せ溶接 
            XStayPlunk    = 39 # ステープランク片面斜角突合せ溶接 
            HeriMiddle    = 40 # ヘリ溶接（中間） 
            Surface       = 41 # サーフェース継手 
            Hold          = 42 # ホルード継手 
            ScurfMiddle   = 43 # スカーフ継手（中間） 
            レSuminiku    = 44 # レ形溶接とすみ肉溶接の組合せ 
            JSuminiku     = 45 # Ｊ形溶接とすみ肉溶接の組合せ 
            SpotMiddle    = 46 # スポット溶接（中間） 
            SimMiddle     = 47 # シム溶接（中間） 
            KeyHole       = 48 # キーホール溶接 
            Stud          = 49 # スタッド溶接 
            Heri          = 50 # ヘリ溶接 
            Scurf         = 51 # スカーフ継手 

        class CircumMark(MyIntEnum):
            NONE     = 1
            CIRF     = 2
            SITE     = 3
            CIRFSITE = 4

        class FaceForm(MyIntEnum):
            NONE = 1
            FLAT = 2
            P    = 3
            H    = 4
            TOE  = 5

        class FinishWay(Enum):
            NONE = ''
            C    = 'C'
            G    = 'G'
            M    = 'M'
            F    = 'F'
            P    = 'P'

        class BackSide(MyIntEnum):
            NONE         = 1
            MeltThtough  = 2
            Backing      = 3

    class Window:
        class Status(MyIntEnum):
            NORMAL = 0
            ICON   = 1
            MAX    = 2

        class View(MyIntEnum):
            TOP    = 1
            FRONT  = 2
            RIGHT  = 3
            LEFT   = 4
            BACK   = 5
            BOTTOM = 6

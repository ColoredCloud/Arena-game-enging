# ==========================================
# 游戏排版与系统配置
# ==========================================
UNIT_SIZE = 40 

LEFT_PANEL_WIDTH = 200
RIGHT_PANEL_WIDTH = 350
ARENA_WIDTH = 500
ARENA_HEIGHT = 600

SCREEN_WIDTH = LEFT_PANEL_WIDTH + ARENA_WIDTH + RIGHT_PANEL_WIDTH
SCREEN_HEIGHT = ARENA_HEIGHT

ARENA_MARGIN = 40
ARENA_LEFT = LEFT_PANEL_WIDTH + ARENA_MARGIN
ARENA_RIGHT = LEFT_PANEL_WIDTH + ARENA_WIDTH - ARENA_MARGIN
ARENA_BOTTOM = ARENA_MARGIN
ARENA_TOP = ARENA_HEIGHT - ARENA_MARGIN

ARENA_CENTER_X = LEFT_PANEL_WIDTH + ARENA_WIDTH / 2
ARENA_CENTER_Y = ARENA_HEIGHT / 2

FACTION_SQUARE = "SQUARE(蓝)"
FACTION_CIRCLE = "CIRCLE(黄)"         
FACTION_TRIANGLE = "TRIANGLE(红)"     

TIER_NORMAL = 1
TIER_ELITE = 2

# ==========================================
# UI & 视觉配置区
# ==========================================
UI_BTN_WIDTH = 160          # 按钮宽度
UI_BTN_HEIGHT = 30          # 按钮高度 (变薄)
UI_BOX_SPACING = 10         # 按钮之间的垂直间距

UI_FONT_TITLE = 16          # 标题大字号
UI_FONT_NORMAL = 12         # 普通信息字号
UI_FONT_SMALL = 10          # 附加细节(如能力描述)小字号
UI_LINE_HEIGHT = 35         # 每条信息的垂直行距

# ==========================================
# 兵种属性数值配置区
# ==========================================

# ----------------- 方块兵 (Square) -----------------
SQ_MAX_HP = 300                    
SQ_SPEED = 3.0 * UNIT_SIZE         
SQ_SKILL_INTERVAL = 2.5            
SQ_SHOCKWAVE_START_RAD = 0         
SQ_SHOCKWAVE_MAX_RAD = 3 * UNIT_SIZE   
SQ_SHOCKWAVE_DURATION = 0.3        
SQ_BASE_DMG = 11                    
SQ_GROWTH_DMG = 5                  
SQ_BASE_DOT_DPS = 2                
SQ_GROWTH_DOT_DPS = 1            
SQ_BASE_DOT_DUR = 3                
SQ_GROWTH_DOT_DUR = 2              

# ----------------- 空心方块兵 (Hollow Square Elite - 蓝精英) -----------------
HSQ_MAX_HP = 700                    
HSQ_SPEED = 3.5 * UNIT_SIZE         
HSQ_CHARGE_CD = 4.0                 
HSQ_DASH_CD = 8.0                  
HSQ_TRAP_CD = 6.0                   
HSQ_DASH_SPEED_MULT = 10.0          

HSQ_CHARGE_COST_DASH = 1            
HSQ_CHARGE_COST_PIERCE = 3          

HSQ_BASE_DOT_DPS = 4.0              
HSQ_GROWTH_DOT_DPS = 1.0            
HSQ_BASE_DOT_DUR = 4.0              
HSQ_GROWTH_DOT_DUR = 2.0            
HSQ_BASE_LIFESTEAL = 0.10           
HSQ_GROWTH_LIFESTEAL = 0.05         

HSQ_SW_WALL = [0.4, 3.0 * UNIT_SIZE, 30, 0.1, 1.0, 2.0]  
HSQ_SW_HIT  = [4.0 * UNIT_SIZE, 30, 0.3, 3.0, 3.0]
HSQ_SW_SEC  = [3.0 * UNIT_SIZE, 30, 0.1, 1.0, 2.0]
HSQ_SW_TRAP = [5.0 * UNIT_SIZE, 30, 0.1, 1.0, 2.0]

# ----------------- 英雄方块 (Point Square Hero - 蓝英雄) -----------------
PSQ_MAX_HP = 600
PSQ_SPEED = 4.0 * UNIT_SIZE
PSQ_BLADE_RADIUS = 3.5 * UNIT_SIZE # 刀的活动边界(仅受此圆限制，不限制于竞技场边界)
PSQ_SHOW_RADIUS = True             # 是否显示警戒圆
PSQ_BLADE_DMG = 10                 # 刀每次穿过造成的伤害
PSQ_HEAL_ON_HIT = 4               # 刀命中时本体的恢复量

# 刀的运动机制 (定期直接转向 + 冲刺减速)
PSQ_BLADE_TURN_CD = 0.4            # 每隔多少秒刀片强制转向直接瞄准敌人
PSQ_BLADE_BURST_SPEED = 30.0 * UNIT_SIZE # 刀片瞄准后的瞬间突刺速度
PSQ_BLADE_MIN_SPEED = 5.0 * UNIT_SIZE    # 刀片减速到的最低速度
PSQ_BLADE_DECEL = 100.0 * UNIT_SIZE       # 刀片穿刺过程中的减速力度

PSQ_BLADE_IDLE_SPEED = 3.0         # 待机环绕角速度
PSQ_HP_THRESHOLDS = [0.6, 0.35, 0.10] # 血量阈值
PSQ_BLADE_COUNTS = [1, 2, 4, 6]    # 不同阈值对应的浮游刃数量
PSQ_BLADE_HIT_CD = 0.1             # 浮游刃对同一目标的伤害冷却

# 特效配置
PSQ_STAR_SPAWN_INTERVAL = 0.07      # 攻击时星星尾迹的生成间隔(控制稀疏程度)
PSQ_BLADE_TRAIL_CONFIG = [0.001, 3]  # 常规曲线尾迹配置：[持续时间(秒), 粗细(像素)]

# 减速控制区
PSQ_AURA_SLOW_MULT = 0.7           # 场地减速乘区：只要在警戒圆内就会持续受到该减速
PSQ_HIT_SLOW_MULT = 0.4            # 命中减速乘区：被刀切中瞬间附加的强力减速
PSQ_HIT_SLOW_DUR = 1.0             # 命中减速的持续时间

# 本体移动追踪配置
PSQ_HOMING_ACCEL = 40.0 * UNIT_SIZE # 本体命中目标后的追踪切向加速度
PSQ_HOMING_DUR = 1.0                # 本体追踪加速持续时间

# ----------------- 骑士方块 (Knight Square) -----------------
KSQ_MAX_HP = 750
KSQ_SPEED = 2.5 * UNIT_SIZE
KSQ_SKILL_CD = 4.0
KSQ_MARK_COUNT = 3                 # 标记的敌人数量(召唤的星星数量)
KSQ_STAR_DMG = 40                  # 星星坠落的基础伤害
KSQ_STAR_RAD = 15                  # 巨大的四角星星视觉半径
KSQ_SW_RAD = 4.0 * UNIT_SIZE       # 下砸冲击波的影响范围

KSQ_STAR_INITIAL_SPEED = 0.0 * UNIT_SIZE # 星星刚召唤时的初速度
KSQ_STAR_ACCEL = 20.0 * UNIT_SIZE        # 星星下坠的重力加速度 (越落越快)

KSQ_BASE_DOT_DPS = 4.0             # 基础毒伤 DPS
KSQ_GROWTH_DOT_DPS = 2.0
KSQ_BASE_DOT_DUR = 3.0             # 基础毒伤持续时间
KSQ_GROWTH_DOT_DUR = 1.0
KSQ_BASE_LIFESTEAL = 0.15          # 基础毒伤吸血率
KSQ_GROWTH_LIFESTEAL = 0.05

KSQ_EXP_STAR_COUNT = 30            # 每次爆炸产生的碎屑星星数量
KSQ_EXP_STAR_MIN_SPEED = 10.0 * UNIT_SIZE  # 碎屑爆开的最小初速度
KSQ_EXP_STAR_MAX_SPEED = 20.0 * UNIT_SIZE # 碎屑爆开的最大初速度
KSQ_EXP_STAR_MIN_SIZE = 8          # 碎屑星星最小尺寸 (新增)
KSQ_EXP_STAR_MAX_SIZE = 16         # 碎屑星星最大尺寸 (新增)
KSQ_EXP_STAR_DURATION = 1.0        # 碎屑存浮渐隐时间
KSQ_EXP_STAR_DRAG = 4.0

# ----------------- 圆形兵 (Circle) -----------------
CR_MAX_HP = 200                    
CR_SPEED = 2.0 * UNIT_SIZE         
CR_SPIKE_CD = 0.1                  
CR_SPIKE_DMG = 15                   
CR_SPIKE_SPEED = 6 * UNIT_SIZE     
CR_SPIKE_RADIUS = 5                

# ----------------- 空心圆形兵 (Hollow Circle Elite) -----------------
HCR_MAX_HP = 500                   
HCR_SPEED = 4.0 * UNIT_SIZE        
HCR_SPIKE_CD = 0.1                 
HCR_SPIKE_DMG = 20                 
HCR_SPIKE_SPEED = 25.0 * UNIT_SIZE 
HCR_SPIKE_RADIUS = 8               
HCR_MARK_APPLY_CD = 5.0            
HCR_MARK_FIRE_CD = 1.0             
HCR_SLOW_RADIUS = 2.5 * UNIT_SIZE  
HCR_SLOW_MULT = 0.5                
HCR_SLOW_DUR = 3.0                 
HCR_REPEL_RADIUS = 2.5 * UNIT_SIZE 
HCR_HEAL_PER_TARGET = 8            
HCR_SCATTER_BUFF_DUR = 3.0         
HCR_BURST_INTERVAL = 0.1           
HCR_MAX_SCATTER_CHARGES = 3        

# ----------------- 实心三角形 (Solid Triangle) -----------------
STR_MAX_HP = 250                   
STR_SPEED = 2.0 * UNIT_SIZE        
STR_MINE_CD = 5.0                  
STR_MINE_DELAY = 5.0               
STR_MINE_RAD = 3.0 * UNIT_SIZE     
STR_MINE_DMG = 35                  
STR_MINE_SLOW = 0.4                

STR_STICKY_CD = 4.0               
STR_STICKY_DELAY = 3.0             
STR_STICKY_RAD = 1.5 * UNIT_SIZE   
STR_STICKY_DMG = 20                
STR_STICKY_SPEED = 8.0 * UNIT_SIZE 

# ----------------- 空心三角形 (Hollow Triangle Elite) -----------------
TR_MAX_HP = 500                    
TR_SPEED = 3.5 * UNIT_SIZE         
TR_GRAPPLE_CD = 12                
TR_GRAPPLE_DUR = 8               
TR_PULSE_CD = 1.5                    
TR_PULSE_RAD = 2 * UNIT_SIZE     
TR_CLEAVE_DIST = 1.6 * UNIT_SIZE     
TR_CLEAVE_DMG = 3                  
TR_ENRAGE_TIME = 30.0              
TR_ENRAGE_DUR = 7                

TR_CLEAVE_INITIAL_CD = 1.0         
TR_CLEAVE_MIN_CD = 0.35             
TR_CLEAVE_MAX_STACKS = 4           
TR_CLEAVE_STACK_DECAY = 5.0        
TR_GRAPPLE_MIN_DIST = 1.5 * UNIT_SIZE
TR_GRAPPLE_ESC_DMG_MULT = 10.0      
TR_ENRAGE_INVINCIBLE = False        
TR_TRAIL_DURATION = 3.0            
TR_ENRAGE_LIFESTEAL = 0.8          

# ----------------- 英雄圆形兵 (Point Circle Hero) -----------------
PCR_MAX_HP = 600                   
PCR_SPEED = 3.0 * UNIT_SIZE        
PCR_SKILL_CD = 6.0                 
PCR_SPIKE_DMG = 15                 
PCR_SPIKE_SPEED = 8.0 * UNIT_SIZE  
PCR_SPIKE_RADIUS = 6               
PCR_HEAL_ON_HIT = 4               
PCR_SW_RAD = 3.0 * UNIT_SIZE       
PCR_SW_DMG = 15                    
PCR_SW_SLOW = 0.3                  
PCR_SW_DUR = 0.5                   
PCR_SPIKE_COUNT = 11                
PCR_SPIKE_BOUNCES = 3              

# ----------------- 英雄三角形 (Point Triangle Hero - 红英雄) -----------------
PTR_MAX_HP = 500                   
PTR_SPEED = 2.5 * UNIT_SIZE        
PTR_ORBIT_COUNT = 8                
PTR_ORBIT_RADIUS = 6.0 * UNIT_SIZE # 飞刃环绕半径 (绕自身)
PTR_ORBIT_SPEED = 1.5              
PTR_DETECT_RADIUS = 5.0 * UNIT_SIZE
PTR_DASH_SPEED = 30.0 * UNIT_SIZE  
PTR_DASH_CD = 0.7                  
PTR_DASH_DMG = 30                  
PTR_DASH_SLOW = 0.5                
PTR_DASH_SLOW_DUR = 0.7            
PTR_DASH_REPEL = 3              
PTR_DASH_HEAL = 10                 

PTR_BLADE_RADIUS = 10              
PTR_ORBIT_ALPHA = 100              # 飞刃未发射时的半透明度 (0-255)

# ----------------- 三角骑士 (Triangle Knight - 红色新单位) -----------------
TKN_MAX_HP = 500                   
TKN_SPEED = 2.5 * UNIT_SIZE        
TKN_MISSILE_CD = 4.0               
TKN_MISSILE_BASE_COUNT = 1         
TKN_MISSILE_HP_THRESHOLDS = [0.66, 0.33, 0.00] 
TKN_MISSILE_COUNTS = [3, 5, 999]     
TKN_MISSILE_SPEED = 6.0 * UNIT_SIZE
TKN_MISSILE_ACCEL = 50 * UNIT_SIZE 
TKN_MISSILE_DMG = 10               
TKN_MISSILE_RAD = 6                
TKN_SW_RAD = 4.0 * UNIT_SIZE       
TKN_MARK_PER_HIT = 2               
TKN_MARK_MAX = 7                   
TKN_MARK_SLOW_MULT = 0.95           
TKN_MARK_WEAK_MULT = 0.9           
TKN_DETONATE_SW_RAD = 5.0 * UNIT_SIZE 
TKN_DETONATE_DMG = 50              
TKN_DETONATE_MARK = 1
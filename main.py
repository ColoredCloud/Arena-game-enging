import arcade
import arcade.gui
import random
import math
from entities1 import SquareUnit, CircleUnit, HollowCircleUnit, PointCircleUnit, HollowTriangleUnit, SolidTriangleUnit, HollowSquareUnit, Spike, CleaveProjectile, StickyBombProjectile
from entities2 import PointTriangleUnit, TriangleKnightUnit, PointSquareUnit, KnightSquareUnit
from constants import *

class BattleArena(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "八角笼竞技场 - 英雄集结版")
        self.units = []
        self.projectiles = []
        self.effects = []
        self.paused = False
        
        self.text_cache = []
        self.text_idx = 0
        
        self.brawl_modes = ["同阵营一队", "同兵种一队", "完全乱斗"]
        self.current_mode_idx = 0
        self.brawl_mode = self.brawl_modes[self.current_mode_idx]
        
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self._setup_ui_buttons()

    def is_enemy(self, a, b):
        owner_a = getattr(a, 'owner', a)
        owner_b = getattr(b, 'owner', b)

        if owner_a == owner_b:
            return False

        if self.brawl_mode == "完全乱斗":
            return True
        elif self.brawl_mode == "同兵种一队":
            return type(owner_a) != type(owner_b)
        else: 
            return getattr(owner_a, 'faction', None) != getattr(owner_b, 'faction', None)

    def _setup_ui_buttons(self):
        self.v_box = arcade.gui.UIBoxLayout(space_between=UI_BOX_SPACING)

        self.btn_mode = arcade.gui.UIFlatButton(text=f"规则: {self.brawl_mode}", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        def toggle_mode(e):
            self.current_mode_idx = (self.current_mode_idx + 1) % len(self.brawl_modes)
            self.brawl_mode = self.brawl_modes[self.current_mode_idx]
            self.btn_mode.text = f"规则: {self.brawl_mode}"
        self.btn_mode.on_click = toggle_mode
        self.v_box.add(self.btn_mode)

        btn_sq = arcade.gui.UIFlatButton(text="召唤: 普通方块(蓝)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_sq.on_click = lambda e: self.add_unit(SquareUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_sq)

        btn_hsq = arcade.gui.UIFlatButton(text="召唤: 精英方块(蓝)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_hsq.on_click = lambda e: self.add_unit(HollowSquareUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_hsq)
        
        btn_psq = arcade.gui.UIFlatButton(text="召唤: 英雄方块(蓝)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_psq.on_click = lambda e: self.add_unit(PointSquareUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_psq)

        btn_ksq = arcade.gui.UIFlatButton(text="召唤: 骑士方块(蓝)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_ksq.on_click = lambda e: self.add_unit(KnightSquareUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_ksq)

        btn_cr = arcade.gui.UIFlatButton(text="召唤: 普通圆形(黄)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_cr.on_click = lambda e: self.add_unit(CircleUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_cr)

        btn_hcr = arcade.gui.UIFlatButton(text="召唤: 精英圆形(黄)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_hcr.on_click = lambda e: self.add_unit(HollowCircleUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_hcr)
        
        btn_pcr = arcade.gui.UIFlatButton(text="召唤: 英雄圆形(黄)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_pcr.on_click = lambda e: self.add_unit(PointCircleUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_pcr)
        
        btn_str = arcade.gui.UIFlatButton(text="召唤: 普通三角(红)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_str.on_click = lambda e: self.add_unit(SolidTriangleUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_str)

        btn_tr = arcade.gui.UIFlatButton(text="召唤: 精英三角(红)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_tr.on_click = lambda e: self.add_unit(HollowTriangleUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_tr)

        btn_ptr = arcade.gui.UIFlatButton(text="召唤: 英雄三角(红)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_ptr.on_click = lambda e: self.add_unit(PointTriangleUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_ptr)

        btn_tkn = arcade.gui.UIFlatButton(text="召唤: 骑士三角(红)", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        btn_tkn.on_click = lambda e: self.add_unit(TriangleKnightUnit(ARENA_CENTER_X, ARENA_CENTER_Y))
        self.v_box.add(btn_tkn)

        btn_clear = arcade.gui.UIFlatButton(text="清空全部", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        def clear_all(e):
            self.units.clear()
            self.projectiles.clear()
            self.effects.clear()
        btn_clear.on_click = clear_all
        self.v_box.add(btn_clear)
        
        btn_pause = arcade.gui.UIFlatButton(text="暂停 / 恢复", width=UI_BTN_WIDTH, height=UI_BTN_HEIGHT)
        def toggle_pause(e): self.paused = not self.paused
        btn_pause.on_click = toggle_pause
        self.v_box.add(btn_pause)

        anchor = arcade.gui.UIAnchorLayout(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        anchor.add(child=self.v_box, anchor_x="left", anchor_y="top", align_x=20, align_y=-20)
        self.manager.add(anchor)

    def add_unit(self, unit):
        angle = random.uniform(0, 2 * math.pi)
        if isinstance(unit, HollowTriangleUnit): speed = TR_SPEED
        elif isinstance(unit, PointTriangleUnit): speed = PTR_SPEED
        elif isinstance(unit, TriangleKnightUnit): speed = TKN_SPEED
        elif isinstance(unit, SolidTriangleUnit): speed = STR_SPEED
        elif isinstance(unit, PointCircleUnit): speed = PCR_SPEED
        elif isinstance(unit, HollowCircleUnit): speed = HCR_SPEED
        elif isinstance(unit, PointSquareUnit): speed = PSQ_SPEED
        elif isinstance(unit, KnightSquareUnit): speed = KSQ_SPEED
        elif isinstance(unit, HollowSquareUnit): speed = HSQ_SPEED
        elif isinstance(unit, SquareUnit): speed = SQ_SPEED
        else: speed = CR_SPEED
        
        unit.change_x = math.cos(angle) * speed
        unit.change_y = math.sin(angle) * speed
        self.units.append(unit)

    def _draw_cached_text(self, text, x, y, color, size, bold=False):
        if self.text_idx >= len(self.text_cache):
            self.text_cache.append(arcade.Text("", 0, 0, arcade.color.WHITE, 12))
        t = self.text_cache[self.text_idx]
        t.text = text
        t.x = x
        t.y = y
        t.color = color
        t.font_size = size
        t.bold = bold
        t.draw()
        self.text_idx += 1

    def on_draw(self):
        self.clear()
        self.text_idx = 0 
        
        arcade.draw_line(LEFT_PANEL_WIDTH, 0, LEFT_PANEL_WIDTH, SCREEN_HEIGHT, arcade.color.GRAY, 2)
        arcade.draw_line(LEFT_PANEL_WIDTH + ARENA_WIDTH, 0, LEFT_PANEL_WIDTH + ARENA_WIDTH, SCREEN_HEIGHT, arcade.color.GRAY, 2)
        arcade.draw_lrbt_rectangle_outline(ARENA_LEFT, ARENA_RIGHT, ARENA_BOTTOM, ARENA_TOP, arcade.color.WHITE, 2)
        
        for unit in self.units: 
            unit.draw()
            self._draw_cached_text(f"#{unit.uid}", unit.x - 6, unit.y + 12, arcade.color.WHITE, 9, bold=True)
            
        for proj in self.projectiles: proj.draw()
        
        for effect in self.effects: 
            if type(effect).__name__ == 'FloatingNumber':
                effect.draw(self) 
            else:
                effect.draw()
        
        self.manager.draw()
        self.draw_right_panel()

    def draw_right_panel(self):
        sorted_units = sorted(self.units, key=lambda u: u.tier, reverse=True)
        start_x = LEFT_PANEL_WIDTH + ARENA_WIDTH + 10
        start_y = SCREEN_HEIGHT - 30
        
        self._draw_cached_text(f"战场监控 (存活: {len(self.units)})", start_x, start_y, arcade.color.YELLOW, UI_FONT_TITLE, bold=True)
        start_y -= 30

        MAX_DISPLAY = 14
        display_units = sorted_units[:MAX_DISPLAY]
        
        # 预定义精英黄圆的能力文本映射字典
        hcr_ability_map = {
            1: "标记反击", 2: "减速波", 3: "击退波", 4: "多重散射", 5: "连发机枪"
        }

        for i, unit in enumerate(display_units):
            y_pos = start_y - (i * UI_LINE_HEIGHT)
            
            # --- 1. 获取基本单位信息与颜色 ---
            if isinstance(unit, SquareUnit): name_str, c_title, c_desc = "普通方块(蓝)", arcade.color.LIGHT_BLUE, arcade.color.WHITE
            elif isinstance(unit, HollowSquareUnit): name_str, c_title, c_desc = "精英方块(蓝)", arcade.color.CYAN, arcade.color.LIGHT_BLUE
            elif isinstance(unit, PointSquareUnit): name_str, c_title, c_desc = "英雄方块(蓝)", arcade.color.BLUE, arcade.color.LIGHT_BLUE
            elif isinstance(unit, KnightSquareUnit): name_str, c_title, c_desc = "骑士方块(蓝)", arcade.color.DARK_BLUE, arcade.color.LIGHT_BLUE
            elif isinstance(unit, CircleUnit): name_str, c_title, c_desc = "普通圆形(黄)", arcade.color.YELLOW, arcade.color.WHITE
            elif isinstance(unit, HollowCircleUnit): name_str, c_title, c_desc = "精英圆形(黄)", arcade.color.ORANGE, arcade.color.LION
            elif isinstance(unit, PointCircleUnit): name_str, c_title, c_desc = "英雄圆形(黄)", arcade.color.YELLOW, arcade.color.LION
            elif isinstance(unit, SolidTriangleUnit): name_str, c_title, c_desc = "普通三角(红)", arcade.color.RED, arcade.color.WHITE
            elif isinstance(unit, HollowTriangleUnit): name_str, c_title, c_desc = "精英三角(红)", arcade.color.RED, arcade.color.LIGHT_GRAY
            elif isinstance(unit, PointTriangleUnit): name_str, c_title, c_desc = "英雄三角(红)", arcade.color.RED, arcade.color.LION
            elif isinstance(unit, TriangleKnightUnit): name_str, c_title, c_desc = "骑士三角(红)", arcade.color.DARK_RED, arcade.color.LION
            else: name_str, c_title, c_desc = "未知单位", arcade.color.GRAY, arcade.color.GRAY

            info1 = f"#{unit.uid} {name_str}   HP: {unit.hp:.0f}"
            info2 = ""
            info3 = ""

            # --- 2. 获取清晰无简写的文本描述 ---
            if isinstance(unit, HollowTriangleUnit):
                info2 = f"状态: {'🔥 狂暴中 (带吸血)' if unit.is_enraged else '正常'} | 连斩攻速叠加: {unit.cleave_cast_count} 层"
            elif isinstance(unit, PointTriangleUnit):
                idle_count = len([o for o in unit.orbiters if o.state == 'ORBIT' and o.is_alive])
                info2 = f"环绕 {idle_count} 把飞刃"
            elif isinstance(unit, TriangleKnightUnit):
                hp_ratio = unit.hp / unit.max_hp
                cnt = TKN_MISSILE_BASE_COUNT
                if hp_ratio <= TKN_MISSILE_HP_THRESHOLDS[2]: cnt = TKN_MISSILE_COUNTS[2]
                elif hp_ratio <= TKN_MISSILE_HP_THRESHOLDS[1]: cnt = TKN_MISSILE_COUNTS[1]
                elif hp_ratio <= TKN_MISSILE_HP_THRESHOLDS[0]: cnt = TKN_MISSILE_COUNTS[0]
                info2 = f"每次齐射 {cnt} 颗追踪导弹"
            elif isinstance(unit, PointSquareUnit):
                info2 = f"{len(unit.blades)} 个切割点"
            elif isinstance(unit, KnightSquareUnit):
                info2 = f"毒素进化: 伤害+{unit.n_dot_dps} | 持续时间+{unit.n_dot_dur} | 吸血率+{unit.n_lifesteal}"
            elif isinstance(unit, HollowSquareUnit):
                info2 = f"已积攒 {unit.dash_charges} 次冲刺 | 场上已布置 {len(unit.traps)} 个陷阱"
                info3 = f"毒素进化: 伤害+{unit.n_dot_dps} | 持续时间+{unit.n_dot_dur} | 吸血率+{unit.n_lifesteal}"
            elif isinstance(unit, PointCircleUnit):
                info2 = f"兵器库: 当前共有 {len(unit.active_spikes)} 把飞剑在场上持续弹射"
            elif isinstance(unit, HollowCircleUnit):
                info2 = f"升级充能: {unit.hit_count}/3 | 散射充能: {unit.scatter_charges} 次"
                ab_names = [hcr_ability_map[e] for e in sorted(list(unit.gained_effects))]
                info3 = f"已解锁能力: {', '.join(ab_names) if ab_names else '无'}"
            elif isinstance(unit, SquareUnit):
                info2 = f"毒素进化: 伤害+{unit.n_dmg} | 毒伤+{unit.n_dot_dps} | 持续+{unit.n_dot_dur}"

            # --- 3. 绘制文字 ---
            self._draw_cached_text(info1, start_x, y_pos, c_title, UI_FONT_NORMAL, bold=True)
            if info2:
                self._draw_cached_text(info2, start_x, y_pos - 15, c_desc, UI_FONT_SMALL)
            if info3:
                self._draw_cached_text(info3, start_x, y_pos - 28, c_desc, UI_FONT_SMALL)

        if len(sorted_units) > MAX_DISPLAY:
            overflow = len(sorted_units) - MAX_DISPLAY
            y_pos = start_y - (MAX_DISPLAY * UI_LINE_HEIGHT)
            self._draw_cached_text(f"...以及另外 {overflow} 个单位活跃中，请在战场上查看", start_x, y_pos, arcade.color.GRAY, UI_FONT_NORMAL, bold=True)

    def on_update(self, delta_time):
        if self.paused: return

        for unit in self.units:
            if hasattr(unit, 'update_status'): unit.update_status(delta_time, self)

            mult = getattr(unit, 'speed_mult', 1.0)
            unit.x += unit.change_x * mult * delta_time
            unit.y += unit.change_y * mult * delta_time

            hit_wall = False
            nx, ny = 0, 0 

            if unit.x - unit.radius < ARENA_LEFT:
                unit.change_x *= -1
                unit.x = ARENA_LEFT + unit.radius
                hit_wall, nx = True, 1
            elif unit.x + unit.radius > ARENA_RIGHT:
                unit.change_x *= -1
                unit.x = ARENA_RIGHT - unit.radius
                hit_wall, nx = True, -1
                
            if unit.y - unit.radius < ARENA_BOTTOM:
                unit.change_y *= -1
                unit.y = ARENA_BOTTOM + unit.radius
                hit_wall, ny = True, 1
            elif unit.y + unit.radius > ARENA_TOP:
                unit.change_y *= -1
                unit.y = ARENA_TOP - unit.radius
                hit_wall, ny = True, -1

            if hit_wall:
                unit.on_wall_collision(nx, ny, self)
                if getattr(unit, 'mark_owner', None) and unit.mark_owner.is_alive:
                    unit.mark_owner.on_marked_target_collided(unit, self)
                    
            unit.update(delta_time, self)

        for effect in self.effects: effect.update(delta_time)

        for i in range(len(self.units)):
            for j in range(i + 1, len(self.units)):
                u1, u2 = self.units[i], self.units[j]
                dist = math.hypot(u1.x - u2.x, u1.y - u2.y)
                min_dist = u1.radius + u2.radius
                
                if dist < min_dist:
                    overlap = min_dist - dist
                    if dist > 0:
                        nx, ny = (u1.x - u2.x)/dist, (u1.y - u2.y)/dist
                    else:
                        nx, ny = 1, 0
                    
                    u1.x += nx * (overlap / 2)
                    u1.y += ny * (overlap / 2)
                    u2.x -= nx * (overlap / 2)
                    u2.y -= ny * (overlap / 2)
                    
                    rel_vx = u1.change_x - u2.change_x
                    rel_vy = u1.change_y - u2.change_y
                    vel_along_normal = rel_vx * nx + rel_vy * ny
                    
                    if vel_along_normal < 0:
                        v1n = u1.change_x * nx + u1.change_y * ny
                        if v1n < 0:
                            u1.change_x -= 2 * v1n * nx
                            u1.change_y -= 2 * v1n * ny
                            
                        v2n = u2.change_x * (-nx) + u2.change_y * (-ny)
                        if v2n < 0:
                            u2.change_x -= 2 * v2n * (-nx)
                            u2.change_y -= 2 * v2n * (-ny)
                        
                        u1.on_collision(u2, self)
                        u2.on_collision(u1, self)
                        
                        for u in (u1, u2):
                            if getattr(u, 'mark_owner', None) and u.mark_owner.is_alive:
                                u.mark_owner.on_marked_target_collided(u, self)

        for proj in self.projectiles:
            proj.update(delta_time)
            
            if getattr(proj, 'is_orbiting_tri', False):
                pass
            elif getattr(proj, 'has_stuck', False) == False:
                if (proj.x < ARENA_LEFT or proj.x > ARENA_RIGHT or 
                    proj.y < ARENA_BOTTOM or proj.y > ARENA_TOP):
                    proj.is_alive = False
                    continue
                    
            if getattr(proj, 'custom_collision', False):
                continue

            for unit in self.units:
                if self.is_enemy(unit, proj):
                    if math.hypot(proj.x - unit.x, proj.y - unit.y) < unit.radius + proj.radius:
                        if hasattr(proj, 'has_stuck'):
                            if not proj.has_stuck:
                                proj.attached_target = unit
                                proj.has_stuck = True
                                proj.change_x = 0; proj.change_y = 0
                                break 
                        else:
                            unit.take_damage(proj.damage, getattr(proj, 'owner', None), self)
                            if hasattr(proj, 'on_hit'):
                                proj.on_hit(unit, self)
                            elif getattr(proj, 'owner', None) and proj.owner.is_alive and hasattr(proj.owner, 'on_spike_hit'):
                                proj.owner.on_spike_hit(unit, self)
                            if not isinstance(proj, CleaveProjectile):
                                proj.is_alive = False
                                break

        self.units = [u for u in self.units if u.is_alive]
        self.projectiles = [p for p in self.projectiles if p.is_alive]
        self.effects = [e for e in self.effects if e.is_alive]

if __name__ == "__main__":
    game = BattleArena()
    arcade.run()
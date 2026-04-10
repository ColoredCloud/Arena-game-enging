import arcade
import math
import random
from constants import *

class Entity:
    _id_counter = 1

    def __init__(self, faction, hp, x, y):
        self.uid = Entity._id_counter
        Entity._id_counter += 1
        
        self.faction = faction
        self.max_hp = hp
        self.hp = hp
        self.x = x
        self.y = y
        self.change_x = 0
        self.change_y = 0
        self.radius = UNIT_SIZE / 2
        self.is_alive = True
        self.dots = {}
        self.tier = TIER_NORMAL 

        self.speed_mult = 1.0       
        self.slow_timer = 0         
        self.mark_owner = None      
        
        self.is_invincible = False
        self.is_enraged = False
        
        self.dot_acc = 0.0
        self.dot_heal_acc = 0.0 
        self.tick_timer = 0.5   

    def get_base_speed(self):
        cname = type(self).__name__
        if cname == 'HollowTriangleUnit': base_spd = TR_SPEED
        elif cname == 'SolidTriangleUnit': base_spd = STR_SPEED
        elif cname == 'PointTriangleUnit': base_spd = PTR_SPEED
        elif cname == 'TriangleKnightUnit': base_spd = TKN_SPEED
        elif cname == 'HollowCircleUnit': base_spd = HCR_SPEED
        elif cname == 'PointCircleUnit': base_spd = PCR_SPEED
        elif cname == 'HollowSquareUnit': base_spd = HSQ_SPEED
        elif cname == 'PointSquareUnit': base_spd = PSQ_SPEED
        elif cname == 'KnightSquareUnit': base_spd = KSQ_SPEED  
        elif cname == 'SquareUnit': base_spd = SQ_SPEED
        else: base_spd = CR_SPEED

        if getattr(self, 'tkn_marks', 0) > 0:
            base_spd *= (TKN_MARK_SLOW_MULT ** self.tkn_marks)

        return base_spd

    def restore_normal_speed(self):
        if getattr(self, 'is_dashing', False): return
        if getattr(self, 'dash_knockback_owner', None): return 
        
        spd = math.hypot(self.change_x, self.change_y)
        if spd > 0:
            base_spd = self.get_base_speed()
            self.change_x = (self.change_x / spd) * base_spd
            self.change_y = (self.change_y / spd) * base_spd

    def apply_friction(self):
        if getattr(self, 'is_dashing', False): return
        if getattr(self, 'dash_knockback_owner', None): return
        
        spd = math.hypot(self.change_x, self.change_y)
        base_spd = self.get_base_speed()
        if spd > base_spd + 0.1:
            new_spd = max(base_spd, spd * 0.95)
            self.change_x = (self.change_x / spd) * new_spd
            self.change_y = (self.change_y / spd) * new_spd

    def update_status(self, dt, engine):
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0: self.speed_mult = 1.0
            
        if getattr(self, 'dash_knockback_grace', 0) > 0:
            self.dash_knockback_grace -= dt
            
        self.apply_friction() 

        self.tick_timer -= dt
        if self.tick_timer <= 0:
            if self.dot_acc > 0 and engine:
                engine.effects.append(FloatingNumber(self.x, self.y, self.dot_acc, is_heal=False))
                self.dot_acc = 0.0
            if self.dot_heal_acc > 0 and engine:
                engine.effects.append(FloatingNumber(self.x, self.y, self.dot_heal_acc, is_heal=True))
                self.dot_heal_acc = 0.0
            self.tick_timer = 0.5

    def update_dots(self, dt, engine):
        for src_id in list(self.dots.keys()):
            time_left, dps, owner = self.dots[src_id]
            self.take_damage(dps * dt, owner, engine, is_dot=True)
            time_left -= dt
            if time_left <= 0: del self.dots[src_id]
            else: self.dots[src_id][0] = time_left

    def take_damage(self, amount, source_owner=None, engine=None, is_dot=False):
        if self.is_invincible: return

        if source_owner and getattr(source_owner, 'tkn_marks', 0) > 0:
            amount *= (TKN_MARK_WEAK_MULT ** source_owner.tkn_marks)

        actual_damage = min(self.hp, amount)
        self.hp -= actual_damage
        if self.hp <= 0: self.is_alive = False
        
        if source_owner and getattr(source_owner, 'is_alive', False):
            if getattr(source_owner, 'is_enraged', False):
                source_owner.heal(actual_damage * TR_ENRAGE_LIFESTEAL, engine)
            if is_dot and hasattr(source_owner, 'dot_lifesteal'):
                heal_amt = actual_damage * source_owner.dot_lifesteal
                source_owner.hp = min(source_owner.max_hp, source_owner.hp + heal_amt)
                source_owner.dot_heal_acc += heal_amt
                
        if is_dot:
            self.dot_acc += amount
        else:
            if engine and amount > 0:
                engine.effects.append(FloatingNumber(self.x, self.y, amount, is_heal=False))

    def heal(self, amount, engine=None):
        if self.is_alive and amount > 0:
            actual_heal = min(self.max_hp - self.hp, amount)
            if actual_heal > 0:
                self.hp += actual_heal
                if engine:
                    engine.effects.append(FloatingNumber(self.x, self.y, actual_heal, is_heal=True))

    def apply_dot(self, owner, dps, duration):
        self.dots[id(owner)] = [duration, dps, owner]

    def on_collision(self, other, engine): 
        self._handle_knockback_end(other, engine)
        self.restore_normal_speed()

    def on_wall_collision(self, nx, ny, engine): 
        self._handle_knockback_end(None, engine)
        self.restore_normal_speed() 
        
    def _handle_knockback_end(self, other, engine):
        if getattr(self, 'dash_knockback_owner', None) and getattr(self, 'dash_knockback_grace', 0) <= 0:
            owner = self.dash_knockback_owner
            self.dash_knockback_owner = None
            self.restore_normal_speed()
            if hasattr(other, 'restore_normal_speed'):
                other.restore_normal_speed()
            engine.effects.append(CustomShockwave(owner, self.x, self.y, *HSQ_SW_SEC, engine))
    
    def _get_nearest_enemy(self, engine, from_x=None, from_y=None):
        nearest, min_dist = None, float('inf')
        fx = from_x if from_x is not None else self.x
        fy = from_y if from_y is not None else self.y
        for unit in engine.units:
            if engine.is_enemy(self, unit) and unit.is_alive:
                dist = math.hypot(unit.x - fx, unit.y - fy)
                if dist < min_dist:
                    min_dist, nearest = dist, unit
        return nearest

    def draw_health_bar(self):
        if self.hp <= 0: return
        hp_ratio = max(0, self.hp / self.max_hp)
        bar_w = UNIT_SIZE
        bar_h = 6
        bottom = self.y - self.radius - 12
        top = bottom + bar_h
        
        bg_color = (100, 0, 0, 255)
        fg_color = (0, 255, 0, 255)
        
        arcade.draw_lrbt_rectangle_filled(self.x - bar_w/2, self.x + bar_w/2, bottom, top, bg_color)
        fg_w = bar_w * hp_ratio
        if fg_w > 0:
            arcade.draw_lrbt_rectangle_filled(self.x - bar_w/2, self.x - bar_w/2 + fg_w, bottom, top, fg_color)

        marks = getattr(self, 'tkn_marks', 0)
        if marks > 0:
            arcade.draw_text(f"[{marks}]", self.x + bar_w/2 + 5, bottom, arcade.color.DARK_RED, 10, bold=True)

# ================== 冲击波与特效 ==================

class FloatingNumber:
    """性能优化版：不再自我实例化 arcade.Text，而是向引擎申请缓存绘制"""
    def __init__(self, x, y, amount, is_heal=False):
        self.x = x + random.uniform(-15, 15)
        self.y = y + random.uniform(-10, 10)
        self.amount = amount
        self.lifetime = 0.8
        self.max_life = 0.8
        self.vy = 40
        self.is_alive = True
        self.is_heal = is_heal
        
        if is_heal:
            self.text_str = f"+{int(self.amount)}" if self.amount >= 1.0 else f"+{self.amount:.1f}"
            self.color_base = (100, 255, 100) 
        else:
            self.text_str = f"-{int(self.amount)}" if self.amount >= 1.0 else f"-{self.amount:.1f}"
            self.color_base = (255, 200, 200) 

    def update(self, dt):
        self.y += self.vy * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.is_alive = False

    def draw(self, engine=None):
        alpha = int(255 * max(0, self.lifetime / self.max_life))
        color = (self.color_base[0], self.color_base[1], self.color_base[2], alpha)
        if engine:
            # 委托对象池渲染，彻底根除字库内存泄漏！
            engine._draw_cached_text(self.text_str, self.x - 10, self.y, color, 12, bold=True)


class BloodTrail:
    def __init__(self, x, y):
        self.x = x + random.uniform(-15, 15)
        self.y = y + random.uniform(-15, 15)
        self.duration = TR_TRAIL_DURATION  
        self.timer = self.duration
        self.is_alive = True
        self.type = random.choice(['dot', 'line'])
        if self.type == 'line':
            self.ex = self.x + random.uniform(-20, 20)
            self.ey = self.y + random.uniform(-20, 20)
        self.radius = random.uniform(2, 6)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0: self.is_alive = False

    def draw(self):
        alpha = int(255 * max(0, self.timer / self.duration))
        if self.type == 'dot':
            arcade.draw_circle_filled(self.x, self.y, self.radius, (200, 0, 0, alpha))
        else:
            arcade.draw_line(self.x, self.y, self.ex, self.ey, (200, 0, 0, alpha), max(1, int(self.radius/2)))

class EffectShockwave:
    def __init__(self, x, y, max_radius, effect_type, owner, engine):
        self.x, self.y = x, y
        self.max_radius = max_radius
        self.effect_type = effect_type 
        self.owner = owner
        self.engine = engine
        self.duration = 0.3
        self.timer = 0
        self.current_radius = 0 
        self.is_alive = True
        self.hit_targets = set()

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.is_alive = False
            return
        self.current_radius = self.max_radius * (self.timer / self.duration)
        
        for unit in self.engine.units:
            if self.engine.is_enemy(self.owner, unit) and unit.is_alive and unit not in self.hit_targets:
                if math.hypot(self.x - unit.x, self.y - unit.y) <= self.current_radius + unit.radius:
                    self.hit_targets.add(unit)
                    
                    if self.effect_type == 'slow':
                        unit.speed_mult = min(unit.speed_mult, HCR_SLOW_MULT)
                        unit.slow_timer = max(unit.slow_timer, HCR_SLOW_DUR)
                    elif self.effect_type == 'repel':
                        dx, dy = unit.x - self.x, unit.y - self.y
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            speed = math.hypot(unit.change_x, unit.change_y)
                            unit.change_x = (dx/dist) * speed
                            unit.change_y = (dy/dist) * speed
                        if self.owner.is_alive:
                            self.owner.heal(HCR_HEAL_PER_TARGET, self.engine)

    def draw(self):
        base_color = arcade.color.PURPLE if self.effect_type == 'slow' else arcade.color.ORANGE
        alpha = max(0, int(255 * (1 - self.timer / self.duration)))
        final_color = (base_color[0], base_color[1], base_color[2], alpha)
        arcade.draw_circle_outline(self.x, self.y, self.current_radius, final_color, 3)

class CustomShockwave:
    def __init__(self, owner, x, y, max_radius, damage, slow_mult, slow_dur, repel_power, engine):
        self.owner = owner
        self.x, self.y = x, y
        self.max_radius = max_radius
        self.damage = damage
        self.slow_mult = slow_mult
        self.slow_dur = slow_dur
        self.repel_power = repel_power
        self.engine = engine

        self.duration = 0.3
        self.timer = 0
        self.current_radius = 0 
        self.is_alive = True
        self.hit_targets = set()

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.is_alive = False
            return
        self.current_radius = self.max_radius * (self.timer / self.duration)

        for unit in self.engine.units:
            if self.engine.is_enemy(self.owner, unit) and unit.is_alive and unit not in self.hit_targets:
                if math.hypot(self.x - unit.x, self.y - unit.y) <= self.current_radius + unit.radius:
                    self.hit_targets.add(unit)
                    unit.take_damage(self.damage, self.owner, self.engine)
                    
                    if hasattr(self.owner, 'dot_dps') and self.owner.dot_dps > 0:
                        unit.apply_dot(self.owner, self.owner.dot_dps, self.owner.dot_dur)
                    if hasattr(self.owner, 'upgrade_random_stat'):
                        self.owner.upgrade_random_stat()
                    
                    if self.slow_mult < 1.0:
                        unit.speed_mult = min(unit.speed_mult, self.slow_mult)
                        unit.slow_timer = max(unit.slow_timer, self.slow_dur)

                    if self.repel_power > 0:
                        dx, dy = unit.x - self.x, unit.y - self.y
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            speed = max(math.hypot(unit.change_x, unit.change_y), 2.0 * UNIT_SIZE)
                            unit.change_x = (dx/dist) * speed * self.repel_power
                            unit.change_y = (dy/dist) * speed * self.repel_power

    def draw(self):
        alpha = max(0, int(255 * (1 - self.timer / self.duration)))
        arcade.draw_circle_outline(self.x, self.y, self.current_radius, (0, 255, 255, alpha), 3)

class Shockwave:
    def __init__(self, owner, engine):
        self.owner = owner
        self.x, self.y = owner.x, owner.y
        self.duration = SQ_SHOCKWAVE_DURATION
        self.timer = 0
        self.start_radius = SQ_SHOCKWAVE_START_RAD
        self.max_radius = SQ_SHOCKWAVE_MAX_RAD
        self.current_radius = self.start_radius
        self.damage = SQ_BASE_DMG + (SQ_GROWTH_DMG * owner.n_dmg)
        self.dot_dps = SQ_BASE_DOT_DPS + (SQ_GROWTH_DOT_DPS * owner.n_dot_dps)
        self.dot_dur = SQ_BASE_DOT_DUR + (SQ_GROWTH_DOT_DUR * owner.n_dot_dur)
        self.is_alive = True
        self.hit_targets = set()
        self.engine = engine

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.is_alive = False
            return
        progress = self.timer / self.duration
        self.current_radius = self.start_radius + (self.max_radius - self.start_radius) * progress
        for unit in self.engine.units:
            if self.engine.is_enemy(self.owner, unit) and unit.is_alive and unit not in self.hit_targets:
                if math.hypot(self.x - unit.x, self.y - unit.y) <= self.current_radius + unit.radius:
                    unit.take_damage(self.damage, self.owner, self.engine)
                    unit.apply_dot(self.owner, self.dot_dps, self.dot_dur)
                    self.hit_targets.add(unit)
                    self.owner.upgrade_random_stat()

    def draw(self):
        alpha = max(0, int(255 * (1 - self.timer / self.duration)))
        color = (0, 191, 255, alpha)
        arcade.draw_circle_outline(self.x, self.y, self.current_radius, color, 3)

class BombShockwave:
    def __init__(self, owner, x, y, max_radius, damage, slow_mult, engine):
        self.owner = owner
        self.x, self.y = x, y
        self.max_radius = max_radius
        self.damage = damage
        self.slow_mult = slow_mult
        self.engine = engine
        self.duration = 0.3
        self.timer = 0
        self.current_radius = 0
        self.is_alive = True
        self.hit_targets = set()

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.is_alive = False
            return
        self.current_radius = self.max_radius * (self.timer / self.duration)
        for unit in self.engine.units:
            if self.engine.is_enemy(self.owner, unit) and unit.is_alive and unit not in self.hit_targets:
                if math.hypot(self.x - unit.x, self.y - unit.y) <= self.current_radius + unit.radius:
                    self.hit_targets.add(unit)
                    unit.take_damage(self.damage, self.owner, self.engine)
                    if self.slow_mult < 1.0:
                        unit.speed_mult = min(unit.speed_mult, self.slow_mult)
                        unit.slow_timer = max(unit.slow_timer, 3.0) 

    def draw(self):
        alpha = max(0, int(255 * (1 - self.timer / self.duration)))
        arcade.draw_circle_outline(self.x, self.y, self.current_radius, (255, 50, 50, alpha), 4)

class BulletPulseEffect:
    def __init__(self, owner, engine):
        self.owner = owner
        self.x, self.y = owner.x, owner.y
        self.max_radius = TR_PULSE_RAD
        self.duration = 0.5
        self.timer = 0
        self.engine = engine
        self.processed_bullets = set()
        self.is_alive = True
        self.prob = 0.3 if getattr(owner, 'is_enraged', False) else 0.15

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.is_alive = False
            return
        
        current_radius = self.max_radius * (self.timer / self.duration)
        for proj in self.engine.projectiles:
            if proj not in self.processed_bullets and self.engine.is_enemy(self.owner, proj):
                if math.hypot(proj.x - self.x, proj.y - self.y) <= current_radius:
                    self.processed_bullets.add(proj)
                    r = random.random()
                    if r < self.prob:
                        proj.is_alive = False
                    elif r < self.prob * 2:
                        proj.faction = self.owner.faction
                        proj.owner = self.owner 
                        proj.color = arcade.color.RED
                        
                        target = self.owner._get_nearest_enemy(self.engine, from_x=proj.x, from_y=proj.y)
                        if target:
                            dx, dy = target.x - proj.x, target.y - proj.y
                            dist = math.hypot(dx, dy)
                            if dist > 0:
                                speed = math.hypot(proj.change_x, proj.change_y)
                                proj.change_x = (dx/dist) * speed
                                proj.change_y = (dy/dist) * speed

    def draw(self):
        alpha = max(0, int(255 * (1 - self.timer / self.duration)))
        arcade.draw_circle_outline(self.x, self.y, self.max_radius * (self.timer / self.duration), (255, 0, 0, alpha), 4)

# ================== 陷阱与投射物 ==================

class ShockTrap:
    def __init__(self, owner, x, y, engine):
        self.owner = owner
        self.x, self.y = x, y
        self.engine = engine
        self.is_alive = True
        self.radius = 16
        self.trigger_cd = 0

    def update(self, dt):
        if self.trigger_cd > 0:
            self.trigger_cd -= dt
            return

        for unit in self.engine.units:
            dist = math.hypot(self.x - unit.x, self.y - unit.y)
            if dist < self.radius + unit.radius:
                is_dashing_owner = (unit == self.owner and getattr(unit, 'is_dashing', False))
                is_knocked_enemy = (getattr(unit, 'dash_knockback_owner', None) == self.owner)
                
                if is_dashing_owner or is_knocked_enemy:
                    self.engine.effects.append(CustomShockwave(self.owner, self.x, self.y, *HSQ_SW_TRAP, self.engine))
                    self.trigger_cd = 0.5
                    
                    if is_dashing_owner:
                        self.owner.dash_charges += 1
                    break

    def draw(self):
        color = arcade.color.CYAN if int(self.trigger_cd * 10) % 2 == 0 else arcade.color.BLUE
        r = 14.14
        points = ((self.x, self.y + r), (self.x + r, self.y), (self.x, self.y - r), (self.x - r, self.y))
        arcade.draw_polygon_outline(points, color, 2)

class GroundBomb:
    def __init__(self, owner, x, y, engine):
        self.owner = owner
        self.x, self.y = x, y
        self.engine = engine
        self.timer = STR_MINE_DELAY
        self.is_alive = True
        
    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.is_alive = False
            self.engine.effects.append(BombShockwave(self.owner, self.x, self.y, STR_MINE_RAD, STR_MINE_DMG, STR_MINE_SLOW, self.engine))
            
    def draw(self):
        color = arcade.color.DARK_RED if int(self.timer * 4) % 2 == 0 else arcade.color.RED
        arcade.draw_circle_filled(self.x, self.y, 8, color)

class StickyBombProjectile:
    def __init__(self, owner, x, y, dir_x, dir_y, engine):
        self.owner = owner
        self.x, self.y = x, y
        self.change_x = dir_x * STR_STICKY_SPEED
        self.change_y = dir_y * STR_STICKY_SPEED
        self.engine = engine
        self.faction = owner.faction
        self.radius = 6
        self.is_alive = True
        self.damage = 0 
        self.attached_target = None
        self.has_stuck = False
        self.stick_timer = STR_STICKY_DELAY
        self.flight_lifetime = 10.0 

    def update(self, dt):
        if self.has_stuck:
            self.stick_timer -= dt
            if self.stick_timer <= 0:
                self.is_alive = False
                self.engine.effects.append(BombShockwave(self.owner, self.x, self.y, STR_STICKY_RAD, STR_STICKY_DMG, 1.0, self.engine))
                return
            if self.attached_target and self.attached_target.is_alive:
                self.x = self.attached_target.x
                self.y = self.attached_target.y
        else:
            self.flight_lifetime -= dt
            if self.flight_lifetime <= 0:
                self.is_alive = False 
                return
            self.x += self.change_x * dt
            self.y += self.change_y * dt

    def draw(self):
        color = arcade.color.MAROON if int(self.stick_timer * 8) % 2 == 0 else arcade.color.RED
        arcade.draw_circle_filled(self.x, self.y, self.radius, color)

class Spike:
    def __init__(self, owner, x, y, dir_x, dir_y, faction, speed, dmg, radius):
        self.owner = owner
        self.x, self.y = x, y
        self.change_x = dir_x * speed
        self.change_y = dir_y * speed
        self.damage = dmg
        self.faction = faction
        self.radius = radius
        self.is_alive = True
        
        if faction == FACTION_CIRCLE: self.color = arcade.color.YELLOW
        elif faction == FACTION_TRIANGLE: self.color = arcade.color.RED
        else: self.color = arcade.color.WHITE

    def draw(self):
        dist = math.hypot(self.change_x, self.change_y)
        if dist > 0:
            end_x = self.x + (self.change_x / dist) * 15
            end_y = self.y + (self.change_y / dist) * 15
        else:
            end_x, end_y = self.x, self.y
        arcade.draw_line(self.x, self.y, end_x, end_y, self.color, 3)

    def update(self, dt):
        self.x += self.change_x * dt
        self.y += self.change_y * dt

class HeroSpike(Spike):
    def __init__(self, owner, x, y, dx, dy, faction, speed, dmg, radius):
        super().__init__(owner, x, y, dx, dy, faction, speed, dmg, radius)
        self.color = arcade.color.LIGHT_YELLOW
        self.bounces_left = PCR_SPIKE_BOUNCES

    def update(self, dt):
        super().update(dt)
        if self.bounces_left > 0:
            bounced = False
            if self.x - self.radius < ARENA_LEFT:
                self.x = ARENA_LEFT + self.radius
                self.change_x *= -1
                bounced = True
            elif self.x + self.radius > ARENA_RIGHT:
                self.x = ARENA_RIGHT - self.radius
                self.change_x *= -1
                bounced = True

            if self.y - self.radius < ARENA_BOTTOM:
                self.y = ARENA_BOTTOM + self.radius
                self.change_y *= -1
                bounced = True
            elif self.y + self.radius > ARENA_TOP:
                self.y = ARENA_TOP - self.radius
                self.change_y *= -1
                bounced = True

            if bounced:
                self.bounces_left -= 1

    def on_hit(self, target, engine):
        if hasattr(self.owner, 'on_hero_spike_hit') and self.owner.is_alive:
            self.owner.on_hero_spike_hit(self, target, engine)

class CleaveProjectile:
    def __init__(self, owner, x, y, dir_x, dir_y):
        self.owner = owner
        self.x, self.y = x, y
        speed = 10 * UNIT_SIZE
        self.change_x = dir_x * speed
        self.change_y = dir_y * speed
        self.damage = TR_CLEAVE_DMG
        self.faction = owner.faction
        self.radius = 10
        self.is_alive = True
        self.lifetime = 0.2 

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0: self.is_alive = False
        self.x += self.change_x * dt
        self.y += self.change_y * dt

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, arcade.color.DARK_RED)

class Grapple:
    def __init__(self, owner, target, duration, is_enrage=False):
        self.owner = owner
        self.target = target
        self.duration = duration
        self.max_dist = max(math.hypot(target.x - owner.x, target.y - owner.y), TR_GRAPPLE_MIN_DIST)
        self.damage_cd = 0
        self.is_enrage = is_enrage

    def update(self, dt, engine):
        if self.duration is not None:
            self.duration -= dt
            if self.duration <= 0: return False
        if not self.target.is_alive or not self.owner.is_alive: return False

        current_dist = math.hypot(self.target.x - self.owner.x, self.target.y - self.owner.y)
        if current_dist < self.max_dist:
            self.max_dist = max(current_dist, TR_GRAPPLE_MIN_DIST)
        elif current_dist > self.max_dist:
            dx = self.target.x - self.owner.x
            dy = self.target.y - self.owner.y
            if current_dist > 0:
                nx, ny = dx / current_dist, dy / current_dist
            else:
                nx, ny = 1, 0
            self.target.x = self.owner.x + nx * self.max_dist
            self.target.y = self.owner.y + ny * self.max_dist
            
            outward_vel = self.target.change_x * nx + self.target.change_y * ny
            if outward_vel > 0:
                self.target.change_x -= 2 * outward_vel * nx
                self.target.change_y -= 2 * outward_vel * ny
                if self.damage_cd <= 0:
                    dmg = (outward_vel / UNIT_SIZE) * TR_GRAPPLE_ESC_DMG_MULT
                    self.target.take_damage(dmg, self.owner, engine)
                    self.damage_cd = 1.0
                    
        if self.damage_cd > 0: self.damage_cd -= dt
        return True

    def draw(self):
        if self.target.is_alive:
            color = arcade.color.RED if self.is_enrage else arcade.color.WHITE
            arcade.draw_line(self.owner.x, self.owner.y, self.target.x, self.target.y, color, 2)


# ================== 单位定义 ==================

class SquareUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_SQUARE, SQ_MAX_HP, x, y)
        self.timer = 0
        self.interval = SQ_SKILL_INTERVAL
        self.n_dmg = 0
        self.n_dot_dps = 0
        self.n_dot_dur = 0

    def draw(self):
        left, right = self.x - UNIT_SIZE / 2, self.x + UNIT_SIZE / 2
        bottom, top = self.y - UNIT_SIZE / 2, self.y + UNIT_SIZE / 2
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.BLUE)
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        self.timer += dt
        if self.timer >= self.interval:
            self.timer -= self.interval
            engine.effects.append(Shockwave(self, engine))

    def upgrade_random_stat(self):
        stat = random.choice(['dmg', 'dot_dps', 'dot_dur'])
        if stat == 'dmg': self.n_dmg += 1
        elif stat == 'dot_dps': self.n_dot_dps += 1
        elif stat == 'dot_dur': self.n_dot_dur += 1

class HollowSquareUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_SQUARE, HSQ_MAX_HP, x, y)
        self.tier = TIER_ELITE
        self.dash_charge_timer = HSQ_CHARGE_CD
        self.dash_timer = HSQ_DASH_CD
        self.trap_timer = HSQ_TRAP_CD
        self.dash_charges = 0
        self.is_dashing = False
        self.dash_start_pos = (x, y)
        self.traps = []
        
        self.dot_dps = HSQ_BASE_DOT_DPS
        self.dot_dur = HSQ_BASE_DOT_DUR
        self.dot_lifesteal = HSQ_BASE_LIFESTEAL
        self.n_dot_dps = 0
        self.n_dot_dur = 0
        self.n_lifesteal = 0

    def draw(self):
        left, right = self.x - self.radius, self.x + self.radius
        bottom, top = self.y - self.radius, self.y + self.radius
        color = arcade.color.CYAN if self.is_dashing else arcade.color.BLUE
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, color, 4)
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        
        self.trap_timer -= dt
        if self.trap_timer <= 0:
            self.trap_timer = HSQ_TRAP_CD
            trap = ShockTrap(self, self.x, self.y, engine)
            self.traps.append(trap)
            engine.effects.append(trap)
            if len(self.traps) > 3:
                old_trap = self.traps.pop(0)
                old_trap.is_alive = False

        self.dash_charge_timer -= dt
        if self.dash_charge_timer <= 0:
            self.dash_charge_timer = HSQ_CHARGE_CD
            self.dash_charges += 1

        self.dash_timer -= dt
        if self.dash_timer <= 0 and not self.is_dashing:
            self.dash_timer = HSQ_DASH_CD
            self.start_dash()

    def upgrade_random_stat(self):
        stat = random.choice(['dot_dps', 'dot_dur', 'lifesteal'])
        if stat == 'dot_dps': 
            self.n_dot_dps += 1
            self.dot_dps = HSQ_BASE_DOT_DPS + HSQ_GROWTH_DOT_DPS * self.n_dot_dps
        elif stat == 'dot_dur': 
            self.n_dot_dur += 1
            self.dot_dur = HSQ_BASE_DOT_DUR + HSQ_GROWTH_DOT_DUR * self.n_dot_dur
        elif stat == 'lifesteal': 
            self.n_lifesteal += 1
            self.dot_lifesteal = HSQ_BASE_LIFESTEAL + HSQ_GROWTH_LIFESTEAL * self.n_lifesteal

    def start_dash(self):
        self.is_dashing = True
        self.dash_start_pos = (self.x, self.y)
        self.change_x *= HSQ_DASH_SPEED_MULT
        self.change_y *= HSQ_DASH_SPEED_MULT

    def stop_dash(self):
        if not self.is_dashing: return
        self.is_dashing = False
        self.restore_normal_speed()

    def on_wall_collision(self, nx, ny, engine):
        Entity.on_wall_collision(self, nx, ny, engine)
        if self.is_dashing:
            self._handle_dash_bounce(None, engine)

    def on_collision(self, other, engine):
        Entity.on_collision(self, other, engine)
        if self.is_dashing:
            if not engine.is_enemy(self, other):
                self._handle_dash_bounce(other, engine)
            else:
                self._handle_dash_hit(other, engine)

    def _handle_dash_bounce(self, other, engine):
        if other:
            other.restore_normal_speed()
            
        dist = math.hypot(self.x - self.dash_start_pos[0], self.y - self.dash_start_pos[1])
        rad = min(dist * HSQ_SW_WALL[0], HSQ_SW_WALL[1])
        engine.effects.append(CustomShockwave(self, self.x, self.y, rad, *HSQ_SW_WALL[2:], engine))
        
        if self.dash_charges >= HSQ_CHARGE_COST_DASH:
            self.dash_charges -= HSQ_CHARGE_COST_DASH
            self.dash_start_pos = (self.x, self.y)
            target = self._get_nearest_enemy(engine)
            if target:
                dx, dy = target.x - self.x, target.y - self.y
                d = math.hypot(dx, dy)
                if d > 0:
                    self.change_x = (dx/d) * (HSQ_SPEED * HSQ_DASH_SPEED_MULT)
                    self.change_y = (dy/d) * (HSQ_SPEED * HSQ_DASH_SPEED_MULT)
            else:
                self.stop_dash()
        else:
            self.stop_dash()

    def _handle_dash_hit(self, enemy, engine):
        enemy.dash_knockback_owner = self
        enemy.dash_knockback_grace = 0.1
        
        dx, dy = enemy.x - self.x, enemy.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            enemy.change_x = (dx/dist) * (HSQ_SPEED * HSQ_DASH_SPEED_MULT)
            enemy.change_y = (dy/dist) * (HSQ_SPEED * HSQ_DASH_SPEED_MULT)
            
        sw = CustomShockwave(self, self.x, self.y, *HSQ_SW_HIT, engine)
        sw.hit_targets.add(enemy) 
        enemy.take_damage(sw.damage, self, engine)
        if hasattr(self, 'dot_dps') and self.dot_dps > 0:
            enemy.apply_dot(self, self.dot_dps, self.dot_dur)
        if sw.slow_mult < 1.0:
            enemy.speed_mult = min(enemy.speed_mult, sw.slow_mult)
            enemy.slow_timer = max(enemy.slow_timer, sw.slow_dur)
        engine.effects.append(sw)
        
        self.upgrade_random_stat()
        
        if self.dash_charges >= HSQ_CHARGE_COST_PIERCE:
            self.dash_charges -= HSQ_CHARGE_COST_PIERCE
            target = self._get_nearest_enemy(engine)
            if target:
                dx, dy = target.x - self.x, target.y - self.y
                d = math.hypot(dx, dy)
                if d > 0:
                    self.change_x = (dx/d) * (HSQ_SPEED * HSQ_DASH_SPEED_MULT)
                    self.change_y = (dy/d) * (HSQ_SPEED * HSQ_DASH_SPEED_MULT)
            else:
                spd = math.hypot(self.change_x, self.change_y)
                if spd > 0:
                    self.change_x = (self.change_x / spd) * (HSQ_SPEED * HSQ_DASH_SPEED_MULT)
                    self.change_y = (self.change_y / spd) * (HSQ_SPEED * HSQ_DASH_SPEED_MULT)
        else:
            self.stop_dash()

class CircleUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_CIRCLE, CR_MAX_HP, x, y)
        self.cd = CR_SPIKE_CD
        self.current_cd = 0

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, arcade.color.YELLOW)
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        if self.current_cd > 0: self.current_cd -= dt

    def _fire_spike_at_enemy(self, engine):
        if self.current_cd <= 0:
            target = self._get_nearest_enemy(engine)
            if target:
                dx, dy = target.x - self.x, target.y - self.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    dir_x, dir_y = dx / dist, dy / dist
                    spawn_x = self.x + dir_x * self.radius
                    spawn_y = self.y + dir_y * self.radius
                    spike = Spike(self, spawn_x, spawn_y, dir_x, dir_y, self.faction, CR_SPIKE_SPEED, CR_SPIKE_DMG, CR_SPIKE_RADIUS)
                    engine.projectiles.append(spike)
                    self.current_cd = self.cd

    def on_collision(self, other, engine):
        Entity.on_collision(self, other, engine)
        if engine.is_enemy(self, other): self._fire_spike_at_enemy(engine)
        
    def on_wall_collision(self, nx, ny, engine):
        Entity.on_wall_collision(self, nx, ny, engine)
        self._fire_spike_at_enemy(engine)

class PointCircleUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_CIRCLE, PCR_MAX_HP, x, y)
        self.tier = TIER_ELITE
        self.skill_timer = PCR_SKILL_CD
        self.active_spikes = []

    def draw(self):
        arcade.draw_circle_outline(self.x, self.y, self.radius, arcade.color.YELLOW, 4)
        arcade.draw_circle_filled(self.x, self.y, self.radius * 0.3, arcade.color.YELLOW)
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        self.skill_timer -= dt
        if self.skill_timer <= 0:
            self.skill_timer = PCR_SKILL_CD
            self._fire_spikes(engine)

    def _fire_spikes(self, engine):
        self.active_spikes = [s for s in self.active_spikes if s.is_alive]
        angles = [i * (2 * math.pi / PCR_SPIKE_COUNT) for i in range(PCR_SPIKE_COUNT)]
        for ang in angles:
            dx, dy = math.cos(ang), math.sin(ang)
            spawn_x = self.x + dx * self.radius
            spawn_y = self.y + dy * self.radius
            sp = HeroSpike(self, spawn_x, spawn_y, dx, dy, self.faction, PCR_SPIKE_SPEED, PCR_SPIKE_DMG, PCR_SPIKE_RADIUS)
            engine.projectiles.append(sp)
            self.active_spikes.append(sp)

    def on_hero_spike_hit(self, spike, target, engine):
        self.heal(PCR_HEAL_ON_HIT, engine)
        engine.effects.append(CustomShockwave(self, target.x, target.y, PCR_SW_RAD, PCR_SW_DMG, PCR_SW_SLOW, PCR_SW_DUR, 0, engine))
        
        self.active_spikes = [s for s in self.active_spikes if s.is_alive and s != spike]
        
        if self.active_spikes:
            s_redirect = random.choice(self.active_spikes)
            dx, dy = target.x - s_redirect.x, target.y - s_redirect.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                s_redirect.change_x = (dx/dist) * PCR_SPIKE_SPEED
                s_redirect.change_y = (dy/dist) * PCR_SPIKE_SPEED

            s_swap = random.choice(self.active_spikes)
            self.x, self.y, s_swap.x, s_swap.y = s_swap.x, s_swap.y, self.x, self.y


class HollowCircleUnit(CircleUnit):
    def __init__(self, x, y):
        Entity.__init__(self, FACTION_CIRCLE, HCR_MAX_HP, x, y)
        self.tier = TIER_ELITE 
        self.cd = HCR_SPIKE_CD
        self.current_cd = 0
        self.hit_count = 0
        self.gained_effects = set() 
        self.mark_apply_cd = 0
        self.mark_fire_cd = 0
        self.scatter_charges = 0
        self.scatter_buff_timer = 0
        self.active_scatter_count = 0
        self.col_req_arr = [3, 2, 1]
        self.col_burst_arr = [2, 3] 
        self.col_req_idx = 0
        self.col_burst_idx = 0
        self.col_counter = 0
        self.bursts_left = 0
        self.burst_interval_timer = 0
        self.current_burst_spikes = 1

    def draw(self):
        arcade.draw_circle_outline(self.x, self.y, self.radius, arcade.color.YELLOW, 4)
        self.draw_health_bar()

    def update(self, dt, engine):
        super().update(dt, engine)
        if self.mark_apply_cd > 0: self.mark_apply_cd -= dt
        if self.mark_fire_cd > 0: self.mark_fire_cd -= dt
        if self.scatter_buff_timer > 0: self.scatter_buff_timer -= dt
        
        if self.bursts_left > 0:
            self.burst_interval_timer -= dt
            if self.burst_interval_timer <= 0:
                self._execute_fire(engine, extra_count=self.current_burst_spikes - 1)
                self.bursts_left -= 1
                self.burst_interval_timer = HCR_BURST_INTERVAL

    def _execute_fire(self, engine, extra_count=0, target=None):
        if target is None: target = self._get_nearest_enemy(engine)
        if target:
            dx, dy = target.x - self.x, target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                dir_x, dir_y = dx / dist, dy / dist
                spawn_x = self.x + dir_x * self.radius
                spawn_y = self.y + dir_y * self.radius
                for i in range(1 + extra_count):
                    angle_offset = (i - extra_count/2) * 0.2 
                    new_dir_x = dir_x * math.cos(angle_offset) - dir_y * math.sin(angle_offset)
                    new_dir_y = dir_x * math.sin(angle_offset) + dir_y * math.cos(angle_offset)
                    spike = Spike(self, spawn_x, spawn_y, new_dir_x, new_dir_y, self.faction, HCR_SPIKE_SPEED, HCR_SPIKE_DMG, HCR_SPIKE_RADIUS)
                    engine.projectiles.append(spike)

    def on_marked_target_collided(self, target, engine):
        if self.mark_fire_cd <= 0:
            self._execute_fire(engine, target=target)
            self.mark_fire_cd = HCR_MARK_FIRE_CD

    def on_spike_hit(self, target, engine):
        self.hit_count += 1
        if self.hit_count >= 3:
            self.hit_count -= 3
            self._gain_random_effect()

        if 1 in self.gained_effects and self.mark_apply_cd <= 0:
            target.mark_owner = self
            self.mark_apply_cd = HCR_MARK_APPLY_CD
        if 2 in self.gained_effects:
            engine.effects.append(EffectShockwave(self.x, self.y, HCR_SLOW_RADIUS, 'slow', self, engine))
        if 4 in self.gained_effects and self.scatter_buff_timer <= 0:
            self.scatter_charges = min(HCR_MAX_SCATTER_CHARGES, self.scatter_charges + 1)

    def on_collision(self, other, engine): 
        Entity.on_collision(self, other, engine)
        self._handle_hcr_collision(engine)
        
    def on_wall_collision(self, nx, ny, engine): 
        Entity.on_wall_collision(self, nx, ny, engine)
        self._handle_hcr_collision(engine)

    def _handle_hcr_collision(self, engine):
        if 3 in self.gained_effects:
            engine.effects.append(EffectShockwave(self.x, self.y, HCR_REPEL_RADIUS, 'repel', self, engine))
        
        if 4 in self.gained_effects and self.scatter_buff_timer <= 0 and self.scatter_charges > 0:
            self.scatter_buff_timer = HCR_SCATTER_BUFF_DUR
            self.active_scatter_count = self.scatter_charges
            self.scatter_charges = 1
            
        spikes_per_shot = 1 + (self.active_scatter_count if self.scatter_buff_timer > 0 else 0)
        
        is_burst = False
        if 5 in self.gained_effects:
            self.col_counter += 1
            if self.col_counter >= self.col_req_arr[self.col_req_idx]:
                self.col_counter = 0
                is_burst = True

        if self.current_cd <= 0:
            if is_burst:
                self.current_burst_spikes = spikes_per_shot
                burst_times = self.col_burst_arr[self.col_burst_idx]
                self._execute_fire(engine, extra_count=self.current_burst_spikes - 1)
                self.bursts_left = burst_times - 1
                self.burst_interval_timer = HCR_BURST_INTERVAL
            else:
                self._execute_fire(engine, extra_count=spikes_per_shot - 1)
            self.current_cd = self.cd

    def _gain_random_effect(self):
        choice = random.choice([1, 2, 3, 4, 5])
        if choice == 4 and 4 not in self.gained_effects:
            self.scatter_charges = max(self.scatter_charges, 1)
        self.gained_effects.add(choice)
        if choice == 5:
            upgrades = []
            if self.col_req_idx < len(self.col_req_arr) - 1: upgrades.append('req')
            if self.col_burst_idx < len(self.col_burst_arr) - 1: upgrades.append('burst')
            if upgrades:
                upg = random.choice(upgrades)
                if upg == 'req': self.col_req_idx += 1
                else: self.col_burst_idx += 1

class SolidTriangleUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_TRIANGLE, STR_MAX_HP, x, y)
        self.tier = TIER_NORMAL
        self.mine_timer = STR_MINE_CD
        self.sticky_timer = STR_STICKY_CD

    def draw(self):
        r = self.radius * 1.2 
        x1, y1 = self.x, self.y + r
        x2, y2 = self.x - r*0.866, self.y - r/2
        x3, y3 = self.x + r*0.866, self.y - r/2
        arcade.draw_triangle_filled(x1, y1, x2, y2, x3, y3, arcade.color.RED)
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        
        self.mine_timer -= dt
        if self.mine_timer <= 0:
            engine.effects.append(GroundBomb(self, self.x, self.y, engine))
            self.mine_timer = STR_MINE_CD
            
        self.sticky_timer -= dt
        if self.sticky_timer <= 0:
            target = self._get_nearest_enemy(engine)
            if target:
                dx, dy = target.x - self.x, target.y - self.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    engine.projectiles.append(StickyBombProjectile(self, self.x, self.y, dx/dist, dy/dist, engine))
                    self.sticky_timer = STR_STICKY_CD

class HollowTriangleUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_TRIANGLE, TR_MAX_HP, x, y)
        self.tier = TIER_ELITE
        self.grapple_timer = TR_GRAPPLE_CD
        self.normal_grapple = None
        self.enrage_grapple = None
        self.pulse_timer = TR_PULSE_CD
        self.cleave_cd_timer = TR_CLEAVE_INITIAL_CD
        self.cleave_cast_count = 0
        self.cleave_idle_timer = 0 
        self.cleave_alternator = 10 
        self.enrage_cooldown_timer = TR_ENRAGE_TIME
        self.enrage_duration_timer = 0
        self.enrage_action_timer = 0
        self.has_hp_enraged = False
        self.trail_timer = 0 

    def draw(self):
        color = arcade.color.RED
        if self.is_enraged: color = arcade.color.ORANGE_RED 
        r = self.radius * 1.2 
        x1, y1 = self.x, self.y + r
        x2, y2 = self.x - r*0.866, self.y - r/2
        x3, y3 = self.x + r*0.866, self.y - r/2
        arcade.draw_triangle_outline(x1, y1, x2, y2, x3, y3, color, 4)
        
        if self.normal_grapple: self.normal_grapple.draw()
        if self.enrage_grapple: self.enrage_grapple.draw()
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        
        self.enrage_cooldown_timer -= dt
        if not self.is_enraged:
            if self.enrage_cooldown_timer <= 0 or (not self.has_hp_enraged and self.hp <= self.max_hp / 2):
                if self.hp <= self.max_hp / 2: self.has_hp_enraged = True
                self.is_enraged = True
                if TR_ENRAGE_INVINCIBLE:
                    self.is_invincible = True
                self.enrage_duration_timer = TR_ENRAGE_DUR
                self.enrage_action_timer = 0
                self.enrage_cooldown_timer = TR_ENRAGE_TIME 
        else:
            self.trail_timer -= dt
            if self.trail_timer <= 0:
                engine.effects.append(BloodTrail(self.x, self.y))
                self.trail_timer = 0.05
                
            self.enrage_duration_timer -= dt
            if self.enrage_duration_timer <= 0:
                self.is_enraged = False
                self.is_invincible = False
                self.enrage_grapple = None 
            else:
                self.enrage_action_timer -= dt
                if self.enrage_action_timer <= 0:
                    self.enrage_action_timer = 3.0
                    target = self._get_nearest_enemy(engine)
                    if target:
                        dx, dy = target.x - self.x, target.y - self.y
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            speed = math.hypot(self.change_x, self.change_y)
                            self.change_x = (dx/dist) * speed
                            self.change_y = (dy/dist) * speed
                            self.enrage_grapple = Grapple(self, target, duration=None, is_enrage=True)

        self.grapple_timer -= dt
        if self.grapple_timer <= 0:
            target = self._get_nearest_enemy(engine)
            if target:
                self.normal_grapple = Grapple(self, target, duration=TR_GRAPPLE_DUR, is_enrage=False)
            self.grapple_timer = TR_GRAPPLE_CD
            
        if self.normal_grapple:
            if not self.normal_grapple.update(dt, engine): self.normal_grapple = None
        if self.enrage_grapple:
            if not self.enrage_grapple.update(dt, engine): self.enrage_grapple = None

        self.pulse_timer -= dt
        if self.pulse_timer <= 0:
            engine.effects.append(BulletPulseEffect(self, engine))
            self.pulse_timer = TR_PULSE_CD

        self.cleave_cd_timer -= dt
        self.cleave_idle_timer += dt  
        
        if self.cleave_idle_timer >= TR_CLEAVE_STACK_DECAY:
            self.cleave_cast_count = 0 
            
        if self.cleave_cd_timer <= 0:
            target = self._get_nearest_enemy(engine)
            if target and math.hypot(target.x - self.x, target.y - self.y) <= TR_CLEAVE_DIST:
                dx, dy = target.x - self.x, target.y - self.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    dir_x, dir_y = dx/dist, dy/dist
                    perp_x, perp_y = -dir_y, dir_x
                    
                    self.cleave_alternator = -self.cleave_alternator
                    spawn_x = self.x + perp_x * self.cleave_alternator
                    spawn_y = self.y + perp_y * self.cleave_alternator
                    
                    engine.projectiles.append(CleaveProjectile(self, spawn_x, spawn_y, dir_x, dir_y))
                    
                    self.cleave_idle_timer = 0  
                    self.cleave_cast_count += 1
                    
                    if self.cleave_cast_count >= TR_CLEAVE_MAX_STACKS:
                        self.cleave_cd_timer = TR_CLEAVE_MIN_CD
                    else:
                        self.cleave_cd_timer = TR_CLEAVE_INITIAL_CD
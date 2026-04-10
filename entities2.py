import arcade
import math
import random
from constants import *
from entities1 import Entity, BloodTrail

class OrbitTrail:
    """自适应大小的飞刃残影特效"""
    def __init__(self, x, y, base_radius):
        self.x = x + random.uniform(-base_radius*0.8, base_radius*0.8)
        self.y = y + random.uniform(-base_radius*0.8, base_radius*0.8)
        self.duration = 1.0
        self.timer = self.duration
        self.is_alive = True
        self.type = random.choice(['dot', 'line'])
        if self.type == 'line':
            self.ex = self.x + random.uniform(-base_radius*1.5, base_radius*1.5)
            self.ey = self.y + random.uniform(-base_radius*1.5, base_radius*1.5)
        self.radius = random.uniform(base_radius * 0.2, base_radius * 0.5)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0: self.is_alive = False

    def draw(self):
        alpha = int(255 * max(0, self.timer / self.duration))
        if self.type == 'dot':
            arcade.draw_circle_filled(self.x, self.y, self.radius, (255, 50, 50, alpha))
        else:
            arcade.draw_line(self.x, self.y, self.ex, self.ey, (255, 50, 50, alpha), max(1, int(self.radius/2)))

class StarTrail:
    """四角星✦特效拖尾"""
    def __init__(self, x, y):
        self.x = x + random.uniform(-6, 6)
        self.y = y + random.uniform(-6, 6)
        self.duration = 0.6
        self.timer = self.duration
        self.is_alive = True
        self.size = random.uniform(4, 10)
        self.angle = random.uniform(0, 360)

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0: self.is_alive = False

    def draw(self):
        alpha = int(255 * max(0, self.timer / self.duration))
        color = (100, 200, 255, alpha) 
        
        points = []
        for i in range(8):
            r = self.size if i % 2 == 0 else self.size * 0.25
            a = math.radians(self.angle + i * 45)
            points.append((self.x + r * math.cos(a), self.y + r * math.sin(a)))
        
        arcade.draw_polygon_filled(points, color)

class HitStarEffect:
    """骑士星落命中敌人后，附着在敌人身上的纯色渐隐四角星特效"""
    def __init__(self, target):
        self.target = target
        self.x = target.x
        self.y = target.y
        self.duration = 0.8
        self.timer = self.duration
        self.is_alive = True
        self.size = 25  # 巨大尺寸
        self.angle = random.uniform(0, 360) # 初始随机角度

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0: 
            self.is_alive = False
            return
            
        # 跟随目标
        if self.target and self.target.is_alive:
            self.x = self.target.x
            self.y = self.target.y
            
        # 加回稳定的纯色旋转，不带位移偏移，只在原地转动
        self.angle += 90 * dt  

    def draw(self):
        alpha = int(255 * max(0, self.timer / self.duration))
        color = (0, 255, 255, alpha) # 纯净的青蓝色
        
        points = []
        for i in range(8):
            r = self.size if i % 2 == 0 else self.size * 0.3
            a = math.radians(self.angle + i * 45)
            points.append((self.x + r * math.cos(a), self.y + r * math.sin(a)))
        
        # 纯色填充，干净利落
        arcade.draw_polygon_filled(points, color)
class ExplosionStarParticle:
    """骑士星星坠落爆炸后散开的碎星特效"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.duration = KSQ_EXP_STAR_DURATION
        self.timer = self.duration
        self.is_alive = True
        self.size = random.uniform(KSQ_EXP_STAR_MIN_SIZE, KSQ_EXP_STAR_MAX_SIZE)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-200, 200)

        # 瞬间向外爆开的速度
        speed = random.uniform(KSQ_EXP_STAR_MIN_SPEED, KSQ_EXP_STAR_MAX_SPEED)
        direction = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(direction) * speed
        self.vy = math.sin(direction) * speed

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.is_alive = False
            return
            
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.rot_speed * dt
        
        # 空气阻力
        self.vx -= self.vx * KSQ_EXP_STAR_DRAG * dt
        self.vy -= self.vy * KSQ_EXP_STAR_DRAG * dt

    def draw(self):
        alpha = int(255 * max(0, self.timer / self.duration))
        color = (150, 220, 255, alpha) 
        
        points = []
        for i in range(8):
            r = self.size if i % 2 == 0 else self.size * 0.3
            a = math.radians(self.angle + i * 45)
            points.append((self.x + r * math.cos(a), self.y + r * math.sin(a)))
        
        arcade.draw_polygon_filled(points, color)

class BladeLineTrail:
    """常规曲线尾迹"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.duration = PSQ_BLADE_TRAIL_CONFIG[0]
        self.timer = self.duration
        self.radius = PSQ_BLADE_TRAIL_CONFIG[1]
        self.is_alive = True

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0: self.is_alive = False

    def draw(self):
        alpha = int(255 * max(0, self.timer / self.duration))
        arcade.draw_circle_filled(self.x, self.y, self.radius, (100, 200, 255, alpha))

class OrbitingTriangle:
    """环绕红三角英雄公转的飞刃"""
    def __init__(self, owner, angle, engine):
        self.owner = owner
        self.angle = angle
        self.engine = engine
        self.state = 'ORBIT'
        self.orbit_radius = PTR_ORBIT_RADIUS
        self.radius = PTR_BLADE_RADIUS
        
        self.x = self.owner.x + self.orbit_radius * math.cos(self.angle)
        self.y = self.owner.y + self.orbit_radius * math.sin(self.angle)
        
        self.change_x = 0
        self.change_y = 0
        
        self.is_alive = True
        self.faction = owner.faction
        self.hit_targets = set()
        self.trail_timer = 0
        
        self.is_orbiting_tri = True
        self.custom_collision = True

    def update(self, dt):
        if not self.owner.is_alive:
            self.is_alive = False
            return
            
        if self.state == 'ORBIT':
            self.angle += PTR_ORBIT_SPEED * dt
            self.x = self.owner.x + self.orbit_radius * math.cos(self.angle)
            self.y = self.owner.y + self.orbit_radius * math.sin(self.angle)
            
        elif self.state == 'DASH':
            self.x += self.change_x * dt
            self.y += self.change_y * dt
            self.trail_timer -= dt
            if self.trail_timer <= 0:
                self.engine.effects.append(OrbitTrail(self.x, self.y, self.radius))
                self.trail_timer = 0.05
                
            for proj in self.engine.projectiles:
                if proj.is_alive and self.engine.is_enemy(self.owner, proj) and not getattr(proj, 'is_orbiting_tri', False):
                    proj_rad = getattr(proj, 'radius', 5)
                    if math.hypot(self.x - proj.x, self.y - proj.y) < self.radius + proj_rad:
                        proj.is_alive = False 
            
            for unit in self.engine.units:
                if self.engine.is_enemy(self.owner, unit) and unit.is_alive and unit not in self.hit_targets:
                    if math.hypot(self.x - unit.x, self.y - unit.y) < self.radius + unit.radius:
                        self.hit_targets.add(unit)
                        unit.take_damage(PTR_DASH_DMG, self.owner, self.engine)
                        unit.speed_mult = min(unit.speed_mult, PTR_DASH_SLOW)
                        unit.slow_timer = max(unit.slow_timer, PTR_DASH_SLOW_DUR)
                        
                        dx, dy = unit.x - self.x, unit.y - self.y
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            speed = max(math.hypot(unit.change_x, unit.change_y), 2.0 * UNIT_SIZE)
                            unit.change_x = (dx/dist) * speed * PTR_DASH_REPEL
                            unit.change_y = (dy/dist) * speed * PTR_DASH_REPEL
                            
                        self.owner.heal(PTR_DASH_HEAL, self.engine)
            
            dist_to_center = math.hypot(self.x - self.owner.x, self.y - self.owner.y)
            if dist_to_center >= self.orbit_radius:
                dot = self.change_x * (self.x - self.owner.x) + self.change_y * (self.y - self.owner.y)
                if dot > 0:
                    self.state = 'ORBIT'
                    self.angle = math.atan2(self.y - self.owner.y, self.x - self.owner.x)
                    self.x = self.owner.x + self.orbit_radius * math.cos(self.angle)
                    self.y = self.owner.y + self.orbit_radius * math.sin(self.angle)

    def draw(self):
        if self.state == 'ORBIT':
            angle_deg = math.degrees(self.angle) + 90
            alpha = PTR_ORBIT_ALPHA  
        else:
            angle_deg = math.degrees(math.atan2(self.change_y, self.change_x)) - 90
            alpha = 255  
            
        r = self.radius
        r_cos30 = r * 0.866
        
        arcade.draw_triangle_filled(
            self.x + r * math.cos(math.radians(angle_deg + 90)), 
            self.y + r * math.sin(math.radians(angle_deg + 90)),
            self.x + r_cos30 * math.cos(math.radians(angle_deg - 150)), 
            self.y + r_cos30 * math.sin(math.radians(angle_deg - 150)),
            self.x + r_cos30 * math.cos(math.radians(angle_deg - 30)), 
            self.y + r_cos30 * math.sin(math.radians(angle_deg - 30)),
            (255, 0, 0, alpha)
        )


class PointTriangleUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_TRIANGLE, PTR_MAX_HP, x, y)
        self.tier = TIER_ELITE
        self.dash_cd = 0
        self.initialized_orbits = False
        self.orbiters = []

    def draw(self):
        color = arcade.color.RED
        r = self.radius * 1.2 
        x1, y1 = self.x, self.y + r
        x2, y2 = self.x - r*0.866, self.y - r/2
        x3, y3 = self.x + r*0.866, self.y - r/2
        arcade.draw_triangle_outline(x1, y1, x2, y2, x3, y3, color, 4)
        
        arcade.draw_triangle_filled(
            self.x, self.y + r*0.4, 
            self.x - r*0.34, self.y - r*0.2, 
            self.x + r*0.34, self.y - r*0.2, 
            color
        )
        
        arcade.draw_circle_outline(self.x, self.y, PTR_DETECT_RADIUS, (255, 0, 0, 80), 2)
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        
        if not self.initialized_orbits:
            for i in range(PTR_ORBIT_COUNT):
                angle = i * (2 * math.pi / PTR_ORBIT_COUNT)
                orbiter = OrbitingTriangle(self, angle, engine)
                self.orbiters.append(orbiter)
                engine.projectiles.append(orbiter)
            self.initialized_orbits = True
            
        self.dash_cd -= dt
        if self.dash_cd <= 0:
            target = self._get_nearest_enemy(engine)
            if target and math.hypot(target.x - self.x, target.y - self.y) <= PTR_DETECT_RADIUS:
                idle_orbiters = [o for o in self.orbiters if o.state == 'ORBIT' and o.is_alive]
                if idle_orbiters:
                    orb = random.choice(idle_orbiters)
                    orb.state = 'DASH'
                    orb.hit_targets.clear()
                    dx, dy = target.x - orb.x, target.y - orb.y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        orb.change_x = (dx/dist) * PTR_DASH_SPEED
                        orb.change_y = (dy/dist) * PTR_DASH_SPEED
                    self.dash_cd = PTR_DASH_CD


class MarkShockwave:
    def __init__(self, owner, x, y, max_radius, damage, mark_stacks, engine):
        self.owner = owner
        self.x, self.y = x, y
        self.max_radius = max_radius
        self.damage = damage
        self.mark_stacks = mark_stacks
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
                    
                    current_marks = getattr(unit, 'tkn_marks', 0)
                    unit.tkn_marks = current_marks + self.mark_stacks
                    
                    if unit.tkn_marks >= TKN_MARK_MAX:
                        unit.tkn_marks = 0
                        self.engine.effects.append(MarkShockwave(
                            self.owner, unit.x, unit.y, 
                            TKN_DETONATE_SW_RAD, TKN_DETONATE_DMG, TKN_DETONATE_MARK, self.engine
                        ))
                        
                    unit.restore_normal_speed()

    def draw(self):
        alpha = max(0, int(255 * (1 - self.timer / self.duration)))
        arcade.draw_circle_outline(self.x, self.y, self.current_radius, (200, 50, 50, alpha), 3)


class HomingMissile:
    def __init__(self, owner, x, y, vx, vy, engine):
        self.owner = owner
        self.x = x
        self.y = y
        self.change_x = vx
        self.change_y = vy
        self.engine = engine
        self.faction = owner.faction
        self.radius = TKN_MISSILE_RAD
        self.is_alive = True
        self.custom_collision = True 
        self.trail_timer = 0

    def update(self, dt):
        target = self.owner._get_nearest_enemy(self.engine, self.x, self.y)
        if target:
            dx, dy = target.x - self.x, target.y - self.y
            v_mag = math.hypot(self.change_x, self.change_y)
            dist = math.hypot(dx, dy)
            
            if dist > 0 and v_mag > 0:
                target_angle = math.atan2(dy, dx)
                current_angle = math.atan2(self.change_y, self.change_x)
                
                angle_diff = math.atan2(math.sin(target_angle - current_angle), math.cos(target_angle - current_angle))
                accel_mag = (abs(angle_diff) / math.pi) * TKN_MISSILE_ACCEL
                
                sign = 1 if angle_diff > 0 else -1
                nx = -self.change_y / v_mag
                ny = self.change_x / v_mag
                
                self.change_x += sign * nx * accel_mag * dt
                self.change_y += sign * ny * accel_mag * dt
                
                new_v_mag = math.hypot(self.change_x, self.change_y)
                if new_v_mag > 0:
                    self.change_x = (self.change_x / new_v_mag) * v_mag

        self.x += self.change_x * dt
        self.y += self.change_y * dt
        
        self.trail_timer -= dt
        if self.trail_timer <= 0:
            self.engine.effects.append(OrbitTrail(self.x, self.y, self.radius * 2))
            self.trail_timer = 0.05
            
        if (self.x < ARENA_LEFT or self.x > ARENA_RIGHT or 
            self.y < ARENA_BOTTOM or self.y > ARENA_TOP):
            self.is_alive = False
            return
            
        for unit in self.engine.units:
            if self.engine.is_enemy(self.owner, unit) and unit.is_alive:
                if math.hypot(self.x - unit.x, self.y - unit.y) < self.radius + unit.radius:
                    self.is_alive = False
                    self.engine.effects.append(MarkShockwave(
                        self.owner, self.x, self.y, 
                        TKN_SW_RAD, TKN_MISSILE_DMG, TKN_MARK_PER_HIT, self.engine
                    ))
                    break

    def draw(self):
        angle = math.degrees(math.atan2(self.change_y, self.change_x)) - 90
        r = self.radius * 2
        r_cos30 = r * 0.866
        arcade.draw_triangle_filled(
            self.x + r * math.cos(math.radians(angle + 90)), 
            self.y + r * math.sin(math.radians(angle + 90)),
            self.x + r_cos30 * math.cos(math.radians(angle - 150)), 
            self.y + r_cos30 * math.sin(math.radians(angle - 150)),
            self.x + r_cos30 * math.cos(math.radians(angle - 30)), 
            self.y + r_cos30 * math.sin(math.radians(angle - 30)),
            arcade.color.DARK_RED
        )


class TriangleKnightUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_TRIANGLE, TKN_MAX_HP, x, y)
        self.tier = TIER_ELITE
        self.missile_timer = TKN_MISSILE_CD

    def draw(self):
        color = arcade.color.DARK_RED
        r = self.radius * 1.2
        x1, y1 = self.x, self.y + r
        x2, y2 = self.x - r*0.866, self.y - r/2
        x3, y3 = self.x + r*0.866, self.y - r/2
        
        arcade.draw_triangle_outline(x1, y1, x2, y2, x3, y3, color, 4)
        
        cross_r = r * 0.4
        arcade.draw_line(self.x - cross_r, self.y, self.x + cross_r, self.y, color, 3)
        arcade.draw_line(self.x, self.y - cross_r, self.x, self.y + cross_r, color, 3)
        
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        
        self.missile_timer -= dt
        if self.missile_timer <= 0:
            self.missile_timer = TKN_MISSILE_CD
            
            hp_ratio = self.hp / self.max_hp
            count = TKN_MISSILE_BASE_COUNT
            if hp_ratio <= TKN_MISSILE_HP_THRESHOLDS[2]:
                count = TKN_MISSILE_COUNTS[2]
            elif hp_ratio <= TKN_MISSILE_HP_THRESHOLDS[1]:
                count = TKN_MISSILE_COUNTS[1]
            elif hp_ratio <= TKN_MISSILE_HP_THRESHOLDS[0]:
                count = TKN_MISSILE_COUNTS[0]
                
            self._fire_missiles(count, engine)
            
    def _fire_missiles(self, count, engine):
        target = self._get_nearest_enemy(engine)
        if target:
            base_angle = math.atan2(target.y - self.y, target.x - self.x)
        else:
            base_angle = random.uniform(0, 2*math.pi)
            
        spread = math.pi / count
        start_angle = base_angle - (spread * (count - 1)) / 2
        for i in range(count):
            ang = start_angle + i * spread
            vx = math.cos(ang) * TKN_MISSILE_SPEED
            vy = math.sin(ang) * TKN_MISSILE_SPEED
            engine.projectiles.append(HomingMissile(self, self.x, self.y, vx, vy, engine))


class SquareBlade:
    def __init__(self, owner, engine):
        self.owner = owner
        self.x = owner.x
        self.y = owner.y
        self.engine = engine
        self.faction = owner.faction
        self.radius = 4
        self.is_alive = True
        self.custom_collision = True
        self.is_orbiting_tri = True   
        
        self.hit_cooldowns = {} 
        self.turn_timer = 0
        
        self.star_dist_acc = 0.0
        self.angle_offset = random.uniform(0, math.pi * 2)
        
        self.change_x = math.cos(self.angle_offset) * PSQ_BLADE_MIN_SPEED
        self.change_y = math.sin(self.angle_offset) * PSQ_BLADE_MIN_SPEED

    def update(self, dt):
        if not self.owner.is_alive:
            self.is_alive = False
            return

        for k in list(self.hit_cooldowns.keys()):
            self.hit_cooldowns[k] -= dt
            if self.hit_cooldowns[k] <= 0:
                del self.hit_cooldowns[k]
                
        self.turn_timer -= dt

        target = None
        min_dist = float('inf')
        for unit in self.engine.units:
            if self.engine.is_enemy(self.owner, unit) and unit.is_alive:
                dist_to_owner = math.hypot(unit.x - self.owner.x, unit.y - self.owner.y)
                if dist_to_owner <= PSQ_BLADE_RADIUS:
                    dist_to_blade = math.hypot(unit.x - self.x, unit.y - self.y)
                    if dist_to_blade < min_dist:
                        min_dist = dist_to_blade
                        target = unit

        old_x, old_y = self.x, self.y

        if target:
            if self.turn_timer <= 0:
                dx, dy = target.x - self.x, target.y - self.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.change_x = (dx / dist) * PSQ_BLADE_BURST_SPEED
                    self.change_y = (dy / dist) * PSQ_BLADE_BURST_SPEED
                self.turn_timer = PSQ_BLADE_TURN_CD
                
            v_mag = math.hypot(self.change_x, self.change_y)
            if v_mag > PSQ_BLADE_MIN_SPEED:
                new_v = max(PSQ_BLADE_MIN_SPEED, v_mag - PSQ_BLADE_DECEL * dt)
                self.change_x = (self.change_x / v_mag) * new_v
                self.change_y = (self.change_y / v_mag) * new_v

        else:
            self.angle_offset += PSQ_BLADE_IDLE_SPEED * dt
            target_x = self.owner.x + math.cos(self.angle_offset) * (PSQ_BLADE_RADIUS * 0.4)
            target_y = self.owner.y + math.sin(self.angle_offset) * (PSQ_BLADE_RADIUS * 0.4)
            dx = target_x - self.x
            dy = target_y - self.y
            self.change_x = dx * 4
            self.change_y = dy * 4

        self.x += self.change_x * dt
        self.y += self.change_y * dt

        if target:
            dist_moved = math.hypot(self.x - old_x, self.y - old_y)
            
            line_steps = max(1, int(dist_moved / 5.0))
            for i in range(line_steps):
                px = old_x + (self.x - old_x) * (i / line_steps)
                py = old_y + (self.y - old_y) * (i / line_steps)
                self.engine.effects.append(BladeLineTrail(px, py))
            
            self.star_dist_acc += dist_moved
            while self.star_dist_acc >= 15.0:
                self.star_dist_acc -= 15.0
                f = random.random() 
                px = old_x + (self.x - old_x) * f
                py = old_y + (self.y - old_y) * f
                self.engine.effects.append(StarTrail(px, py))

        dist_to_owner = math.hypot(self.x - self.owner.x, self.y - self.owner.y)
        if dist_to_owner > PSQ_BLADE_RADIUS:
            nx = (self.x - self.owner.x) / dist_to_owner
            ny = (self.y - self.owner.y) / dist_to_owner
            self.x = self.owner.x + nx * PSQ_BLADE_RADIUS
            self.y = self.owner.y + ny * PSQ_BLADE_RADIUS
            
            v_dot_n = self.change_x * nx + self.change_y * ny
            if v_dot_n > 0:
                self.change_x -= 2 * v_dot_n * nx
                self.change_y -= 2 * v_dot_n * ny

        for unit in self.engine.units:
            if self.engine.is_enemy(self.owner, unit) and unit.is_alive and unit not in self.hit_cooldowns:
                if math.hypot(self.x - unit.x, self.y - unit.y) < self.radius + unit.radius:
                    unit.take_damage(PSQ_BLADE_DMG, self.owner, self.engine)
                    self.hit_cooldowns[unit] = PSQ_BLADE_HIT_CD
                    
                    unit.speed_mult = min(getattr(unit, 'speed_mult', 1.0), PSQ_HIT_SLOW_MULT)
                    unit.slow_timer = max(getattr(unit, 'slow_timer', 0), PSQ_HIT_SLOW_DUR)
                    
                    self.owner.heal(PSQ_HEAL_ON_HIT, self.engine)
                    
                    if hasattr(self.owner, 'trigger_homing'):
                        self.owner.trigger_homing(unit)

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, arcade.color.LIGHT_BLUE)


class PointSquareUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_SQUARE, PSQ_MAX_HP, x, y)
        self.tier = TIER_ELITE
        self.blades = []
        self.homing_target = None
        self.homing_timer = 0
        
    def trigger_homing(self, target):
        self.homing_target = target
        self.homing_timer = PSQ_HOMING_DUR

    def draw(self):
        r = self.radius
        color = arcade.color.CYAN if self.homing_timer > 0 else arcade.color.BLUE
        arcade.draw_lrbt_rectangle_outline(self.x - r, self.x + r, self.y - r, self.y + r, color, 4)
        inner_r = r * 0.4
        arcade.draw_lrbt_rectangle_filled(self.x - inner_r, self.x + inner_r, self.y - inner_r, self.y + inner_r, color)
        
        if PSQ_SHOW_RADIUS:
            arcade.draw_circle_outline(self.x, self.y, PSQ_BLADE_RADIUS, (0, 0, 255, 60), 2)
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)

        for unit in engine.units:
            if engine.is_enemy(self, unit) and unit.is_alive:
                dist = math.hypot(unit.x - self.x, unit.y - self.y)
                if dist <= PSQ_BLADE_RADIUS:
                    unit.speed_mult = min(getattr(unit, 'speed_mult', 1.0), PSQ_AURA_SLOW_MULT)
                    unit.slow_timer = max(getattr(unit, 'slow_timer', 0), 0.2)

        if self.homing_timer > 0:
            self.homing_timer -= dt
            if self.homing_target and self.homing_target.is_alive:
                dx, dy = self.homing_target.x - self.x, self.homing_target.y - self.y
                dist = math.hypot(dx, dy)
                v_mag = math.hypot(self.change_x, self.change_y)
                
                if dist > 0 and v_mag > 0:
                    target_angle = math.atan2(dy, dx)
                    current_angle = math.atan2(self.change_y, self.change_x)
                    angle_diff = math.atan2(math.sin(target_angle - current_angle), math.cos(target_angle - current_angle))
                    accel_mag = (abs(angle_diff) / math.pi) * PSQ_HOMING_ACCEL
                    
                    sign = 1 if angle_diff > 0 else -1
                    nx = -self.change_y / v_mag
                    ny = self.change_x / v_mag
                    
                    self.change_x += sign * nx * accel_mag * dt
                    self.change_y += sign * ny * accel_mag * dt
                    
                    self.change_x += (self.change_x / v_mag) * (PSQ_HOMING_ACCEL * 0.5) * dt
                    self.change_y += (self.change_y / v_mag) * (PSQ_HOMING_ACCEL * 0.5) * dt
            else:
                self.homing_timer = 0 

        hp_ratio = self.hp / self.max_hp
        target_count = PSQ_BLADE_COUNTS[0]
        if hp_ratio <= PSQ_HP_THRESHOLDS[2]: target_count = PSQ_BLADE_COUNTS[3]
        elif hp_ratio <= PSQ_HP_THRESHOLDS[1]: target_count = PSQ_BLADE_COUNTS[2]
        elif hp_ratio <= PSQ_HP_THRESHOLDS[0]: target_count = PSQ_BLADE_COUNTS[1]

        self.blades = [b for b in self.blades if b.is_alive]
        while len(self.blades) < target_count:
            blade = SquareBlade(self, engine)
            self.blades.append(blade)
            engine.projectiles.append(blade)


# ================== 骑士方块专属类 (蓝骑士) ==================

class StarShockwave:
    """坠落星星下砸触发的冲击波"""
    def __init__(self, owner, x, y, max_radius, damage, engine):
        self.owner = owner
        self.x, self.y = x, y
        self.max_radius = max_radius
        self.damage = damage
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
                        
                    # 触发随动纯色指示特效
                    self.engine.effects.append(HitStarEffect(unit))

    def draw(self):
        alpha = max(0, int(255 * (1 - self.timer / self.duration)))
        arcade.draw_circle_outline(self.x, self.y, self.current_radius, (0, 255, 255, alpha), 3)


class FallingStar:
    """骑士方块召唤的从天而降的旋转星星，带重力加速和爆碎特效"""
    def __init__(self, owner, target_x, target_y, engine):
        self.owner = owner
        self.target_x = target_x
        self.target_y = target_y
        self.engine = engine
        self.faction = owner.faction
        self.radius = KSQ_STAR_RAD
        
        self.x = target_x
        self.y = ARENA_TOP + 100
        
        self.change_x = 0
        self.change_y = -KSQ_STAR_INITIAL_SPEED  
        
        self.is_alive = True
        self.custom_collision = True 
        self.is_orbiting_tri = True  
        
        self.angle = random.uniform(0, 360)
        self.trail_timer = 0

    def update(self, dt):
        if not self.owner.is_alive:
            self.is_alive = False
            return
            
        self.change_y -= KSQ_STAR_ACCEL * dt
        
        self.y += self.change_y * dt
        self.angle += 360 * dt  
        
        self.trail_timer -= dt
        if self.trail_timer <= 0:
            self.engine.effects.append(StarTrail(self.x, self.y))
            self.trail_timer = 0.05
            
        if self.y <= self.target_y:
            self.is_alive = False
            
            self.engine.effects.append(StarShockwave(
                self.owner, self.target_x, self.target_y,
                KSQ_SW_RAD, KSQ_STAR_DMG, self.engine
            ))
            
            for _ in range(KSQ_EXP_STAR_COUNT):
                self.engine.effects.append(ExplosionStarParticle(self.target_x, self.target_y))

    def draw(self):
        arcade.draw_circle_outline(self.target_x, self.target_y, KSQ_SW_RAD, (0, 200, 255, 60), 2)
        
        points = []
        for i in range(8):
            r = self.radius if i % 2 == 0 else self.radius * 0.3
            a = math.radians(self.angle + i * 45)
            points.append((self.x + r * math.cos(a), self.y + r * math.sin(a)))
        arcade.draw_polygon_filled(points, arcade.color.LIGHT_BLUE)
        arcade.draw_polygon_outline(points, arcade.color.BLUE, 2)


class KnightSquareUnit(Entity):
    def __init__(self, x, y):
        super().__init__(FACTION_SQUARE, KSQ_MAX_HP, x, y)
        self.tier = TIER_ELITE
        self.skill_timer = KSQ_SKILL_CD
        
        self.dot_dps = KSQ_BASE_DOT_DPS
        self.dot_dur = KSQ_BASE_DOT_DUR
        self.dot_lifesteal = KSQ_BASE_LIFESTEAL
        
        self.n_dot_dps = 0
        self.n_dot_dur = 0
        self.n_lifesteal = 0

    def draw(self):
        r = self.radius
        color = arcade.color.DARK_BLUE
        
        arcade.draw_lrbt_rectangle_outline(self.x - r, self.x + r, self.y - r, self.y + r, color, 4)
        
        arcade.draw_line(self.x - r*0.6, self.y, self.x + r*0.6, self.y, color, 3)
        arcade.draw_line(self.x, self.y - r*0.6, self.x, self.y + r*0.6, color, 3)
        
        self.draw_health_bar()

    def update(self, dt, engine):
        self.update_status(dt, engine)
        self.update_dots(dt, engine)
        
        self.skill_timer -= dt
        if self.skill_timer <= 0:
            self.skill_timer = KSQ_SKILL_CD
            
            enemies = [u for u in engine.units if engine.is_enemy(self, u) and u.is_alive]
            if enemies:
                targets = random.sample(enemies, min(KSQ_MARK_COUNT, len(enemies)))
                for target in targets:
                    engine.projectiles.append(FallingStar(self, target.x, target.y, engine))

    def upgrade_random_stat(self):
        stat = random.choice(['dot_dps', 'dot_dur', 'lifesteal'])
        if stat == 'dot_dps': 
            self.n_dot_dps += 1
            self.dot_dps = KSQ_BASE_DOT_DPS + KSQ_GROWTH_DOT_DPS * self.n_dot_dps
        elif stat == 'dot_dur': 
            self.n_dot_dur += 1
            self.dot_dur = KSQ_BASE_DOT_DUR + KSQ_GROWTH_DOT_DUR * self.n_dot_dur
        elif stat == 'lifesteal': 
            self.n_lifesteal += 1
            self.dot_lifesteal = KSQ_BASE_LIFESTEAL + KSQ_GROWTH_LIFESTEAL * self.n_lifesteal
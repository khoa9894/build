import json
import random
import math
import csv
import os

class LevelGenerator:
    def __init__(self, level: int):
        self.level = level
        self.difficulty = self._calculate_difficulty(level)
        self._grid_height, self._grid_width = self._generate_grid_size()
        self.theme = self._generate_theme()
        self.tile_data = self._generate_tiles_and_specials()
        self._time = self._time_estimate()
        self.gravity = self._generate_gravity()
    def _circle(self):
        if self.difficulty <5:
            return False
        return True
    def _generate_gravity(self):
        if self.level <= 5:
            return 0
        
        if self.difficulty < 2:
            return 0
        
        
        return random.randint(1, 4)
    
    def _time_estimate(self):
        if self._grid_width*self._grid_height<20:
            return 60
        elif self._grid_width*self._grid_height<40:
            return 90
        else: return 120
    
    def _calculate_difficulty(self, level: int):
        cycle = 20
        pos_in_cycle = level % cycle
        if pos_in_cycle <= cycle // 2:
            return pos_in_cycle / 2.0
        else:
            return (cycle - pos_in_cycle) / 2.0
    
    def _generate_grid_size(self):
        base_height = 3 + int(self.difficulty * 0.8)
        base_width = 4 + int(self.difficulty * 0.8)
        
        level_cycle = self.level % 20  
        level_phase = self.level % 10 
        
        # Level-based adjustments
        height_adjustment = 0
        width_adjustment = 0
        
        # Tăng size theo từng milestone level
        if self.level > 80:
            height_adjustment += 2
            width_adjustment += 2
        elif self.level > 60:
            height_adjustment += 1.5
            width_adjustment += 1.5
        elif self.level > 40:
            height_adjustment += 1
            width_adjustment += 1
        elif self.level > 20:
            height_adjustment += 0.5
            width_adjustment += 0.5
        
        if level_phase <= 2: 
            height_adjustment -= 0.3
            width_adjustment -= 0.2
        elif level_phase >= 7: 
            height_adjustment += 0.3
            width_adjustment += 0.5
        
        height = int(base_height + height_adjustment)
        width = int(base_width + width_adjustment)
        
        if random.random() < 0.3:  
            height += random.choice([0, 1])
            width += random.choice([0, 1])
        
        max_height = min(8, 6 + (self.level // 25)) 
        max_width = min(12, 8 + (self.level // 20))  
        
        height = max(3, min(height, max_height))
        width = max(4, min(width, max_width))
        
        return self._ensure_even_tiles(height, width, max_height, max_width)
    
    def _ensure_even_tiles(self, height, width, max_height, max_width):
        while True:
            total_tiles = height * width
            if total_tiles % 2 == 0:
                return height, width
            
            if width < max_width:
                width += 1
            elif height < max_height:
                height += 1
            else:
                if width > height + 2:  
                    width = max(4, width - 1)
                elif height > width + 1:  
                    height = max(3, height - 1)
                else:
                    if random.choice([True, False]):
                        width = max(4, width - 1)
                    else:
                        height = max(3, height - 1)
    
    def _generate_theme(self):
        themes = ['FRUIT', 'BUTTERFLY', 'DRINK', 'CAKE']
        
        return random.choice(themes)
    
    def _generate_tiles_and_specials(self):
        total_tiles = self._grid_height * self._grid_width
        
        max_specials = min(total_tiles // 4, 8) 
        
        rocket_base_ratio = 0.2 + 0.05 * self.difficulty
        level_bonus = min(0.1, self.level * 0.001)  
        rocket_ratio = min(0.4, rocket_base_ratio + level_bonus)
        
        num_rocket_tiles = max(0, round(max_specials * rocket_ratio))
        if num_rocket_tiles % 2 != 0:
            num_rocket_tiles = max(0, num_rocket_tiles - 1)
        
        bomb_ratio = 0.1 + 0.06 * self.difficulty
        if self.level > 50:
            bomb_ratio += 0.05
        bomb_ratio = min(bomb_ratio, 0.5)
        
        max_bombs = min((total_tiles - num_rocket_tiles) // 4, 10)
        num_bomb_effects = round(max_bombs * bomb_ratio)
        
        if self.level < 4:
            num_bomb_effects = 0
        
        remaining_tiles = total_tiles - num_rocket_tiles 
        
        num_tile_types = self._calculate_num_tile_types()
        selected_tile_types = list(range(num_tile_types))
        tile_distribution = self._distribute_normal_tiles(remaining_tiles, selected_tile_types)
        
        return {
            'TotalTiles': total_tiles,
            'RocketTiles': num_rocket_tiles,
            'BombEffects': num_bomb_effects,
            'TileDistribution': tile_distribution
        }
    
    def _calculate_num_tile_types(self):
        base_types = 3
        
        if self.level <= 5:
            base_types = 3
        elif self.level <= 15:
            base_types = 4
        elif self.level <= 30:
            base_types = 5
        elif self.level <= 50:
            base_types = 6
        elif self.level <= 75:
            base_types = 7
        else:
            base_types = 8
        
        difficulty_bonus = int(self.difficulty * 0.5)
        base_types += difficulty_bonus
        
        level_phase = self.level % 10
        if level_phase <= 2:  
            base_types -= 1
        elif level_phase >= 8: 
            base_types += 1
        
        return max(3, min(8, base_types))
    
    def _distribute_normal_tiles(self, total_normal_tiles, tile_types):
        num_types = len(tile_types)
        min_pairs_per_type = 1
        base_tiles = min_pairs_per_type * 2 * num_types
        
        if total_normal_tiles < base_tiles:
            pairs_per_type = max(1, total_normal_tiles // (2 * num_types))
            remaining = total_normal_tiles - (pairs_per_type * 2 * num_types)
            
            distribution = {}
            for i, tile_type in enumerate(tile_types):
                count = pairs_per_type * 2
                if i < remaining // 2:
                    count += 2
                distribution[tile_type] = count
            return distribution
        
        distribution = {tile_type: min_pairs_per_type * 2 for tile_type in tile_types}
        remaining_tiles = total_normal_tiles - base_tiles
        extra_pairs = remaining_tiles // 2
        
        pairs_per_type = extra_pairs // num_types
        leftover_pairs = extra_pairs % num_types
        
        for tile_type in tile_types:
            distribution[tile_type] += pairs_per_type * 2
        
        leftover_types = random.sample(tile_types, min(leftover_pairs, len(tile_types)))
        for tile_type in leftover_types:
            distribution[tile_type] += 2
        
        return distribution
    
    def export_level_data(self):
        return {
            'Level': self.level,
            'Difficulty': self.difficulty,
            'GridHeight': self._grid_height,
            'GridWidth': self._grid_width,
            'Theme': self.theme,
            'Tiles': {
                'TotalTiles': self.tile_data['TotalTiles'],
                'RocketTiles': self.tile_data['RocketTiles'],
                'BombEffects': self.tile_data['BombEffects'],
                'NormalTiles': self.tile_data['TileDistribution']
            },
            'Time': self._time,
            'Gravity': self.gravity,
            'Circle': self._circle()
        }
    
    def save_to_file(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.export_level_data(), f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    levels = []
    for i in range(1, 101):
        generator = LevelGenerator(i)
        generator.save_to_file(f"map/level{i}.json")
        data = generator.export_level_data()
        tiles = data['Tiles']
        normal_sum = sum(tiles['NormalTiles'].values()) if isinstance(tiles['NormalTiles'], dict) else 0
        levels.append({
            'Level': data['Level'],
            'GridHeight': data['GridHeight'],
            'GridWidth': data['GridWidth'],
            'TotalTiles': tiles['TotalTiles'],
            'RocketTiles': tiles['RocketTiles'],
            'BombEffects': tiles['BombEffects'],
            'NormalTilesSum': normal_sum,
            'Difficulty': generator.difficulty,
            'Time': data['Time'],
            'Gravity': data['Gravity'],
            'Circle':data['Circle']
        })

    with open('levels_summary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Level', 'GridHeight', 'GridWidth', 'TotalTiles', 'RocketTiles', 'BombEffects', 'NormalTilesSum', 'Difficulty', 'Time', 'Gravity','Circle']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in levels:
            writer.writerow(row)

    print("Generated 100 levels and levels_summary.csv successfully!")
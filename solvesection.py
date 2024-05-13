import numpy as np
import pandas as pd
import random
from copy import deepcopy


class Layer():
    def __init__(self, material_table_row):
        self.name = material_table_row['mat_name']
        self.sn = material_table_row['sn']
        self.cost = material_table_row['cost']
        self.density = material_table_row['density']
        self.unit = material_table_row['unit']
        surface = material_table_row['surface']
        subgrade = material_table_row['subgrade']
        alkaline = material_table_row['alkaline']
        minimum_lift = material_table_row['min']
        self.min_lift = minimum_lift
        self.thickness = minimum_lift
        self.max_lift = material_table_row['max']
        self.cost_per_inch = self.calc_cost_per_inch()
        self.surface_code = 1 if surface == "Yes" else 0
        self.subgrade_code = 1 if subgrade == "Yes" else 0
        self.alkaline_code = 1 if alkaline == "Yes" else 0
        self.cost_per_sn = self.cost_per_inch / self.sn
        return None

    def calc_cost_per_inch(self):
        if self.unit == "ton":
            tonnage = self.density * 27 / 2000
            cost_per_sy = self.cost * tonnage / 36 # in per yd
            return cost_per_sy
        elif self.unit == "cyd":
            cost_per_sy = self.cost / 36
            return cost_per_sy
        elif self.unit == "sqyd":
            return self.cost / self.min_lift
        else:
            return 0.0

class Section(list): # subclass list just for sanity
    def __init__(self, *layers):
        super().__init__(*layers)

def make_material_list(material_table):
    return [Layer(row) for row in material_table]


def make_trial_section(material_list) -> Section:
    # select 1-4 materials at random and save to an array
    num_materials: int = np.random.randint(1, 5)
    section = Section()
    for _ in range(num_materials):
        section.append(deepcopy(random.choice(material_list)))
    section.sort(key = lambda l : l.surface_code)
    section.reverse()
    section.sort(key = lambda l : l.subgrade_code)
    return section


def validate_section(section):
    # no duplicate courses of materials
    names = [l.name for l in section]
    if len(names) != len(set(names)):
        return False
    # must have a surface course
    if section[0].surface_code == 0:
        return False
    # cannot have multiple subgrade treatments
    if sum([l.subgrade_code for l in section]) > 1:
        return False
    # cannot have adjacent alkaline courses
    alk = np.array([l.alkaline_code for l in section])
    alk_roll = np.roll(alk, 1)
    if np.logical_and(alk, alk_roll).any():
        return False
    # thickness must be a positive number
    if any([l.thickness <= 0 for l in section]):
        return False
    # thickness must be achievable within lift size limits
    for l in section:
        if not l.thickness % l.min_lift < l.max_lift-l.min_lift or l.thickness % l.max_lift == 0:
            return False
    return True

def remove_duplicate_sections(section_list):
    result_list = []
    used_combinations = set()
    for section in section_list:
        names = [l.name for l in section]
        names.sort()
        if tuple(names) in used_combinations:
            continue
        result_list.append(section)
        used_combinations.add(tuple(names))
    return result_list


def section_sn(section):
    return sum([l.sn * l.thickness for l in section])


def section_cost(section, grade, embankment_cost, excavation_cost):
    earthwork_per_inch = lambda e: e / 36
    total_thickness = sum([l.thickness for l in section])
    subgrade_elevation = grade - total_thickness
    earthwork = 0.0
    if subgrade_elevation > 0:
        earthwork = earthwork_per_inch(embankment_cost) * subgrade_elevation
    if subgrade_elevation < 0:
        earthwork = earthwork_per_inch(excavation_cost) * subgrade_elevation
    return sum([l.cost_per_inch * l.thickness for l in section]) + earthwork


def modify_thickness(section, goal_sn):
    epsilon = 0.01
    current_sn = section_sn(section)
    cost_index = [(i,l) for i,l in enumerate(section)]
    cost_index.sort(key=lambda x: x[1].cost_per_sn)
    increment_size = lambda l: 0.5 if l.min_lift < 2.0 else 1.0
    for _ in range(10):  # this may not benefit from multiple passes
        delta = goal_sn - current_sn
        if abs(delta) < epsilon:
            break
        for i,_l in cost_index:
            layer = section[i]
            if layer.min_lift == layer.max_lift:
                continue # pass layers with fixed thickness
            inc = increment_size(layer)
            inc_sn_delta = layer.sn * inc
            adjustment = delta // inc_sn_delta if delta > 0 else np.ceil(delta / inc_sn_delta)
            layer.thickness += inc * adjustment
            if layer.thickness <= layer.min_lift:
                layer.thickness = layer.min_lift
            current_sn = section_sn(section)
            delta = goal_sn - current_sn
    return section


def solve(material_table, goal_sn, grade=0.0, embankment_cost=0.0, excavation_cost=0.0):
    # this seems like it could be better.
    material_list = make_material_list(material_table)
    sample_population = 5000
    trial_sections = [make_trial_section(material_list) for _ in range(sample_population)]
    unique_sections = remove_duplicate_sections(trial_sections)
    valid_sections = [s for s in unique_sections if validate_section(s)]
    modified_sections = [modify_thickness(s, goal_sn) for s in valid_sections]
    revalidated_sections = [s for s in modified_sections if validate_section(s)]
    revalidated_sections.sort(key=lambda s: section_cost(s, grade, embankment_cost, excavation_cost))
    return revalidated_sections

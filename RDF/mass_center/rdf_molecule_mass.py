import mdtraj as md
import numpy as np  
import os
import os.path
import pandas as pd
import openpyxl as pxl
from statistics import mean
from math import sqrt

def dis(ref, tag):
    x = ref[0] - tag[0]
    y = ref[1] - tag[1]
    z = ref[2] - tag[2]
    return sqrt(x**2 + y**2 + z**2)

n_frames = 200

mass = {
    'C': 12,
    'H': 1,
    'O': 16,
    'N': 14,
    'S': 32,
    'F': 19,
    'Cl': 35.45
}

for filename in os.listdir('./'):
    if filename.endswith('.pdb'):
        excipient_name = filename[17:-4]
        traj = md.load(filename)
        top = traj.topology
        ori = 0
        total = np.zeros(16 * n_frames)
        
        length_drug = top.residue(0).n_atoms
        length_excp = top.residue(12).n_atoms
        
        ele_mass_drug = []
        ele_mass_excp = []
        
        for i in range(length_drug):
            element = str(top.residue(0).atom(i).element.symbol)
            ele_mass_drug.append(mass[element])
        mass_drug = sum(ele_mass_drug)
        
        for i in range(length_excp):
            element = str(top.residue(12).atom(i).element.symbol)
            ele_mass_excp.append(mass[element])
        mass_excp = sum(ele_mass_excp)
        
        mass_part = mass_drug * 12 + mass_excp * 4
        
        for i in range(n_frames):
            start = 0
            position = np.zeros((17,3))
            for j in range(16):
                res = top.residue(j)
                length = res.n_atoms
                
                x = list(traj.xyz[i, start:start + length, 0])
                y = list(traj.xyz[i, start:start + length, 1])
                z = list(traj.xyz[i, start:start + length, 2])
                
                lst_x, lst_y, lst_z = [], [], []

                for h in range(length):
                    if j <= 11:
                        lst_x.append(x[h] * ele_mass_drug[h] / mass_drug)
                        lst_y.append(y[h] * ele_mass_drug[h] / mass_drug)
                        lst_z.append(z[h] * ele_mass_drug[h] / mass_drug)

                    else:
                        lst_x.append(x[h] * ele_mass_excp[h] / mass_excp)
                        lst_y.append(y[h] * ele_mass_excp[h] / mass_excp)
                        lst_z.append(z[h] * ele_mass_excp[h] / mass_excp)
                
                position[j][:] = sum(lst_x), sum(lst_y), sum(lst_z)
                start += length

            lst_p_x, lst_p_y, lst_p_z = [], [], []

            for j in range(16):
                if j <= 11:
                    lst_p_x.append(position[j][0] * mass_drug)
                    lst_p_y.append(position[j][1] * mass_drug)
                    lst_p_z.append(position[j][2] * mass_drug)
                else:
                    lst_p_x.append(position[j][0] * mass_excp)
                    lst_p_y.append(position[j][1] * mass_excp)
                    lst_p_z.append(position[j][2] * mass_excp)

            x_p = sum(lst_p_x) / mass_part
            y_p = sum(lst_p_y) / mass_part
            z_p = sum(lst_p_z) / mass_part

            position[-1][:] = x_p, y_p, z_p
            
            distance = np.zeros(16)
            for h in range(16):
                distance[h] = dis(position[-1], position[h])
            
            total[ori:ori + 16] = distance
            ori += 16
            
        r_range = np.array([0, 5])
        bin_width = 0.05
        n_bins = int((r_range[1] - r_range[0]) / bin_width)
        g_r, edges = np.histogram(total, range=r_range, bins=n_bins)
        g_r = g_r / (16 * n_frames)
        r = 0.5 * (edges[1:] + edges[:-1])

        df = pd.DataFrame({'r': r, 'g_r': g_r})
        
        if not os.path.isfile('rdf_molecule_mass.xlsx'):
            df.to_excel('rdf_molecule_mass.xlsx', '%s' % excipient_name, index = True)
        
        else:
            excel_book = pxl.load_workbook('rdf_molecule_mass.xlsx')
            with pd.ExcelWriter('rdf_molecule_mass.xlsx', engine = 'openpyxl') as writer:
                writer.book = excel_book
                writer.sheets = {worksheet.title: worksheet for worksheet in excel_book.worksheets}
                df.to_excel(writer, '%s' % excipient_name, index = True)
                writer.save()

import os
import os.path
import mdtraj as md
import numpy as np
import pandas as pd
import openpyxl as pxl
import statistics

n_frames = 20000
for filename in os.listdir('./'):
    if filename.endswith('.pdb'):
        excipient_name = filename[17:-4]
        RMSD_1 = np.zeros(n_frames)
        RMSD_2 = np.zeros(n_frames)
        AVERAGE = np.zeros(n_frames)
        mean = np.zeros(n_frames)
        sd = np.zeros(n_frames)

        traj_1 = md.load(filename, atom_indices = np.arange(0,48))
        traj_2 = md.load(filename, atom_indices = np.arange(48,96))

        last_traj_1 = traj_1.slice(n_frames-1)
        last_traj_2 = traj_2.slice(n_frames-1)

        RMSD_1 = md.rmsd(traj_1, last_traj_1)
        RMSD_2 = md.rmsd(traj_2, last_traj_2)

        for i in range(n_frames):
            AVERAGE[i] = (RMSD_1[i] + RMSD_2[i])/2

        mean[0] = statistics.mean(AVERAGE)
        sd[0] = statistics.stdev(AVERAGE)
        df = pd.DataFrame({'RMSD_1': RMSD_1, 'RMSD_2': RMSD_2, 'AVERAGE': AVERAGE, 'Mean': mean, 'SD': sd})

        if not os.path.isfile('convergence_results.xlsx'):
            df.to_excel('convergence_results.xlsx', '%s' % excipient_name, index = False)

        else:
            excel_book = pxl.load_workbook('convergence_results.xlsx')
            with pd.ExcelWriter('convergence_results.xlsx', engine = 'openpyxl') as writer:
                writer.book = excel_book
                writer.sheets = {worksheet.title: worksheet for worksheet in excel_book.worksheets}
                df.to_excel(writer, '%s' % excipient_name, index = False)
                writer.save()

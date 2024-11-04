import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid formal string')
    return template, outtype, annotation_classes

def infotodict(seqinfo):
    t1w_mprage = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w-mprage_NC')
    t1w_cube = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w-cube_NC')
    t1w_space = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w-space_NC')
    t1w_bravo = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w-bravo_NC')

    t1wPC_mprage = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w-mprage-CE')
    t1wPC_mprage_orig = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w-mprage-CE_orig')
    t1wPC_cube = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w-cube-CE')
    t1wPC_space = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w-space-CE')

    t2w_cube = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T2w-cube')
    t2w_propeller = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T2w-propeller')
    t2w_tse = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T2w-tse')
    t2w_flair = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T2w-flair')

    cord_t1w = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_cord-t1w')
    cord_t1w_PC = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_cord-t1w-PC')
    
    cord_t2w = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_cord-t2w_part-{item:03d}')
    cord_t2w_PC = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_cord-t2w-PC')

    dwi_64dir = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_dwi')
    dwi_B0s = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-B0s-dwi')

    DTI_klinisk = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_DTI')
    DTI_klinisk_orig = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_DTI_orig')
    DTI_AP_B0 = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_DTI_ABCD_B0')
    DTI_ABCD = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_DTI_ABCD')
    DTI_multishell = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_DTI_multishell')

    QSM_postprocessed = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_QSM_post')
    R2_star = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_R2*')
    SWI_qsm = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_SWI_true')
    SWI_mIP_qsm = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_SWI_mIP_true')
    MAG_qsm = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_MAG_true')

    SWI_swan = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_SWI_swan')

    fMRI_rs = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_rest-rsfMRI')
    fMRI_rs_fm = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_rest-rsfMRI_fieldmap')

    ASL = create_key('sub-{subject}/{session}/perf/sub-{subject}_{session}_ASL')

    info = {
        t1w_mprage: set(),
        t1w_cube: set(),
        t1w_space: set(),
        t1w_bravo: set(),

        t1wPC_mprage: set(),
        t1wPC_mprage_orig: set(),
        t1wPC_cube: set(),
        t1wPC_space: set(),

        t2w_cube: set(),
        t2w_propeller: set(),
        t2w_tse: set(),
        t2w_flair: set(),

        cord_t1w: set(),
        cord_t1w_PC: set(),
        
        #cord_t2w has identical names which are enumerated
        cord_t2w: set(),
        cord_t2w_PC: set(),

        dwi_64dir: set(),
        dwi_B0s: set(),

        DTI_klinisk: set(),
        DTI_klinisk_orig: set(),
        DTI_AP_B0: set(),
        DTI_ABCD: set(),
        DTI_multishell: set(),

        QSM_postprocessed: set(),
        R2_star: set(),
        SWI_qsm: set(),
        SWI_mIP_qsm: set(),
        MAG_qsm: set(),

        SWI_swan: set(),

        fMRI_rs_fm: set(),
        fMRI_rs: set(),

        ASL: set(),
    }
    
    processed_series = set()
    
    # Separate IF statement for scanners
    for s in seqinfo:
        if s.series_description == 'T1MRAGE_08iso' or s.series_description == 'T1MPRAGE' or s.series_description == 't1_mprage_sag_p2_iso_1.0 (Rek. 2mm ax+cor)':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t1w_mprage].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'Sag T1 Cube':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t1w_cube].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 't1_space_sag_p2_iso_1.0':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t1w_space].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'FSPGR BRAVO' or s.series_description == 'FSPGR_SAG_TI450':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t1w_bravo].add(s.series_id)
            processed_series.add(s.series_description)

        elif s.series_description == 'T1MRAGE_08iso_K+':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t1wPC_mprage].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'ORIG T1MRAGE_08iso_K+':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t1wPC_mprage_orig].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'Sag T1 Cube K+':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t1wPC_cube].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'Sag_t1spc_iso0.9_p2_tr500_ce':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t1wPC_space].add(s.series_id)
            processed_series.add(s.series_description)

        elif s.series_description == 'T2CUBE_08iso' or s.series_description == 'T2CUBE':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t2w_cube].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'Ax T2 PROPELLER' or s.series_description == 'T2 Propeller':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t2w_propeller].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'Tra_TSE_T2_3mm' or s.series_description == 't2_tse_tra_4mm' or s.series_description == 't2_tse_tra_p2 4mm':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t2w_tse].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'FLAIRopt_HS12' or s.series_description == 'Sag T2 FLAIR Cube' or s.series_description == 'Sag_Flair_spc_iso_0.48' or s.series_description == 'sag_T2_3d_CUBE_flair' or s.series_description == 't2_space_dark-fluid_sag_p2_iso' or s.series_description == 't2_space_flair_sag_p2_iso_1.0' or s.series_description == 'Sag FLAIR CUBE':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[t2w_flair].add(s.series_id)
            processed_series.add(s.series_description)

        elif s.series_description == 'Sag T2 FRFSE':
            info[cord_t2w].add(s.series_id)
            processed_series.add(s.series_description)

        elif s.series_description == 'Tra_DWI_resolve_b0_1000_3.5mm' or s.series_description == 'Tra_DWI_resolve_b0_1000_3.5mm_TRACEW' or s.sequence_name == '*re_b0':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[dwi_64dir].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'Ax DWI MUSE B1000' or s.sequence_name == '*re_b0_1000':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[dwi_B0s].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'Ax DTI klinisk sekvens' or s.series_description == 'Ax DWI til klinisk bruk':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[DTI_klinisk].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'ORIG: Ax DWI til klinisk bruk':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[DTI_klinisk_orig].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'DTI_AP_b0_script':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[DTI_AP_B0].add(s.series_id)
            processed_series.add(s.series_description)
        
        elif s.series_description == 'DTI_PA_ABCD':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[DTI_ABCD].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'MMIL MULTISHELL DIFFUSION':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[DTI_multishell].add(s.series_id)
            processed_series.add(s.series_description)

        elif s.series_description == 'QSM':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[QSM_postprocessed].add(s.series_id)
        
        elif s.series_description == 'R2*':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[R2_star].add(s.series_id)
            
        elif s.series_description == 'SWI':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[SWI_qsm].add(s.series_id)
            
        elif s.series_description == 'SWI mIP':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[SWI_mIP_qsm].add(s.series_id)
            
        elif s.series_description == 'MAG':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[MAG_qsm].add(s.series_id)
            
        elif s.series_description == 'Ax SWAN 3D':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[SWI_swan].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'rsfMRI':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[fMRI_rs].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'rsfMRI_FieldMap':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[fMRI_rs_fm].add(s.series_id)
            processed_series.add(s.series_description)
            
        elif s.series_description == 'ASL':
            if s.series_description in processed_series:
                continue  # Skip if already processed
            info[ASL].add(s.series_id)
            processed_series.add(s.series_description)

    return info

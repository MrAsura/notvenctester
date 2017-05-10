﻿"""
Test suite containing functions for generating test results from TestInstances
"""

import openpyxl as xl
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.formatting.rule import ColorScaleRule
import re
import cfg

__FILE_END = r".xlsm"
__KBS = r"kbs"
__PSNR = r"psnr"
__SCALE = r"scale"
__RES = r"results"

__res_regex = r"\sProcessed\s(\d+)\sframes\sover\s(\d+)\slayer\(s\),\s*(\d+)\sbits\sAVG\sPSNR:\s(\d+[.,]\d+)\s(\d+[.,]\d+)\s(\d+[.,]\d+)"
__lres_regex_format = r"\s\sLayer\s{lid}:\s*(\d+)\sbits,\sAVG\sPSNR:\s(\d+[.,]\d+)\s(\d+[.,]\d+)\s(\d+[.,]\d+)"

__R_HEADER = ["Sequence","Layer"]
__R_HEADER_QP = "QP {}"
__R_KBS = "Kb/s"
__R_PSNR = "PSNR"
__R_PSNR_SUB = ["Y","U","V","AVG"]

__SEQ_FORMAT = "{} @ scale {}"
__PSNR_AVG = "=(6*{y}+{u}+{v})/8"

__C_AVG = r"=AVERAGE({})"
__SEQ_AVERAGE = r"Average"

__S_SEQ_HEADER = "Sequence {} results"
__S_BDRATE_FORMAT = "=bdrate({},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})"
__S_HEADER = "Result summary (bdrate comparisons)"

__SR_FORMAT = r"'{sheet}'!{cell}"

__LID_TOT = -1

__LAYER2TEST_SEP = r"_layer"
__LAYER2TEST_FORMAT = r"{test}"+ __LAYER2TEST_SEP + "{lid}"

__COMBI_SEP = "+"

"""
Generate sheet layer string
"""
def makeSheetLayer(sheet,layer):
    return __LAYER2TEST_FORMAT.format(test=sheet,lid=layer)

"""
Parse sheet layer string
"""
def parseSheetLayer(string):
    return string.split(sep=__LAYER2TEST_SEP)

def parseCombiName(string):
    return string.split(sep=__COMBI_SEP)

def makeCombiName(combi):
    return __COMBI_SEP.join(combi)

"""
Parse kb/s from test results 
"""
def __parseKBS(res,lres,trgt,nl):
    #TODO: Parse separate layers
    (frames,bits) = res.group(1,3)
    lframes = int(frames)/nl
    for lid in range(nl):
        if lres[lid]:
            lbits = lres[lid].group(1)
            trgt[lid][__KBS] = float(lbits)/float(lframes)
        else:
            trgt[lid][__KBS] = float(bits)/float(frames)
    trgt[__LID_TOT][__KBS] = float(bits)/float(frames)

"""
Parse psnr from test results
"""
def __parsePSNR(res,lres,trgt,nl):
    #TODO: Parse separate layers
    for lid in range(nl):
        if lres[lid]:
            trgt[lid][__PSNR] = lres[lid].group(2,3,4)
        else:
            trgt[lid][__PSNR] = res.group(4,5,6)
    trgt[__LID_TOT][__PSNR] = res.group(4,5,6)

"""
Parse needed values
"""
def __parseVals(res):
    trgt = {}
    res_ex = re.search(__res_regex, str(res))
    lres_ex = []
    num_layers = int(res_ex.group(2))
    for lid in range(num_layers):
        lres_ex.append(re.search(__lres_regex_format.format(lid=lid), str(res)))
        trgt[lid] = {}
    trgt[__LID_TOT] = {}
    __parseKBS(res_ex,lres_ex,trgt,num_layers)
    __parsePSNR(res_ex,lres_ex,trgt,num_layers)
    return trgt


"""
Parse test results
@return a dict with parsed results
"""
def __parseTestResults(tests):
    results = {}
    for test in tests:
        main_res = {}
        
        # For each sequence
        for (seq,qps) in test._results.items():
            main_res[seq] = {}
            # For each qp
            for (qp,res) in qps.items():
                qp_res = __parseVals(res)

                # Set qp results
                main_res[seq][qp] = qp_res
        # Set base results
        results[test._test_name] = {__RES: main_res, __SCALE: str(test._input_layer_scales)}

    return results

"""
Combine psnr and kbs values
"""
def __combiValues(vals):
   
    res = {__RES:{},__SCALE:''}
    #Init structure
    for (seq,qps) in vals[0][__RES].items():
        res[__RES][seq] = {}
        for (qp,lids) in qps.items():
            res[__RES][seq][qp] = {}
            for (lid,val) in lids.items():
                res[__RES][seq][qp][lid] = {}
                res[__RES][seq][qp][lid][__KBS] = 0
                res[__RES][seq][qp][lid][__PSNR] = (0,0,0)

    numv = len(vals)

    scales = []
    for item in vals:
        scales.append(item[__SCALE])
        for (seq,qps) in item[__RES].items():
            for (qp,lids) in qps.items():
                for (lid,val) in lids.items():
                    res[__RES][seq][qp][lid][__KBS] += val[__KBS]
                    res[__RES][seq][qp][lid][__PSNR] = tuple(map(lambda x,y: float(y) + float(x)/float(numv), val[__PSNR], res[__RES][seq][qp][lid][__PSNR]))
    res[__SCALE] = makeCombiName(scales)
        
    return res

"""
Combine test results to form new tests
@param combi: list of results to combine  (or list of lists). 
"""
def __combiTestResults(results, combi):
    res = results.copy()

    for set in combi:
        vals = []
        for item in set:
            vals.append(results[item])
        cname = makeCombiName(set)
        res[cname] = __combiValues(vals)

    return res
    

"""
Write summary base header
@return row and col of start of data field
"""
def __writeSummaryMatrixHeader(sheet, tests, row, col):
    d_row = row + 1
    d_col = col + 1
    #Write horizontal headers/test names
    tmp_col = col + 1
    for test in tests:
        sheet.cell(row = row, column = tmp_col).value = test
        tmp_col += 1

    #Write vertical 
    tmp_row = row + 1
    for test in tests:
        sheet.cell(row = tmp_row, column = col).value = test
        tmp_row += 1

    return d_row, d_col

"""
Write summary matrix data
"""
def __writeSummaryMatrix(sheet, data, row, col):
    test_col = col - 1
    test_row = row - 1
    final_r = row+len(data.keys())
    final_c = col+len(data.keys())
    for r in range(row,row+len(data.keys())):
        for c in range(col,col+len(data.keys())):
            t2 = sheet.cell(row = r, column = test_col).value
            t1 = sheet.cell(row = test_row, column = c).value
            if t1 == t2:
                sheet.cell(row = r, column = c).value = "-"
            else:
                #TODO: Handle layers
                r1 =[__SR_FORMAT.format(sheet=parseSheetLayer(t1)[0],cell=cl) for cl in data[t1][__KBS] + data[t1][__PSNR]]
                r2 =[__SR_FORMAT.format(sheet=parseSheetLayer(t2)[0],cell=cl) for cl in data[t2][__KBS] + data[t2][__PSNR]]
                sheet.cell(row = r, column = c).value = __S_BDRATE_FORMAT.format(*(r1+r2))
                sheet.cell(row = r, column = c).style = 'Percent'
            sheet.cell(row=r,column=c).alignment = xl.styles.Alignment(horizontal='center')
    # Set conditional coloring
    form_range = "{}:{}".format(get_column_letter(col)+str(row),get_column_letter(final_c)+str(final_r))
    sheet.conditional_formatting.add(form_range,
                                     ColorScaleRule(start_type='percentile', start_value=90, start_color='63BE7B',
                                                    mid_type='num', mid_value=0, mid_color='FFFFFF',
                                                    end_type='percentile', end_value=10, end_color='F8696B' ))


"""
Write summary sheet
"""
def __writeSummary(sheet, ref_pos):

    seq_ref = {}

    # Init structure for each sequence
    for (test,item) in ref_pos.items():
        for seq in item.keys():
            seq_ref[seq] = {}
    # Populate
    for (test,item) in ref_pos.items():
        for (seq,val) in item.items():
            seq_ref[seq][test] = val
    #print(seq_ref)
    # For each sequence generate the comparison matrix
    sheet.cell(row = 1, column = 1).value = __S_HEADER 
    for (seq,ref) in seq_ref.items():
        tests = sorted(ref.keys())
        # write matrix
        row = sheet.max_row + 2
        col = 1 #sheet.max_column + 1
        sheet.cell(row = row, column = col).value = __S_SEQ_HEADER.format(seq)
        (row, col) = __writeSummaryMatrixHeader(sheet, tests, row+1, col)
        __writeSummaryMatrix(sheet, ref, row, col)

    # Make columns wider
    for col in range(sheet.max_column):
        sheet.column_dimensions[get_column_letter(col+1)].width = 15


"""
Transform res_pos into summary test structure
"""
def __makeSummary(res_pos,layers={}):
    res = {}
    for (test,item) in res_pos.items():
        res[test] = {}
        for (seq,vals) in item.items():
            test_in_layers = test in layers
            if not test_in_layers:
                res[test][seq] = vals[__LID_TOT]
                if len(vals.keys()) <= 2: #If only 2 lids, it should mean the total layer and other layer are the same
                    continue
            for (lid,val) in vals.items():
                if lid == __LID_TOT and not test_in_layers:
                    continue
                if test_in_layers and lid not in layers[test]:
                    continue
                nn = makeSheetLayer(test,lid)
                if lid == __LID_TOT or len(vals.keys()) <= 2:
                    nn = test
                if nn in res:
                    res[nn][seq] = val
                else:
                    res[nn] = {seq:val}

    return res

"""
Write results for a single test/sheet
@return positions of relevant cells
"""
def __writeSheet(sheet,data,scale):
    # Write header
    for col in range(len(__R_HEADER)):
        sheet.cell(row = 1, column = col+1).value = __R_HEADER[col]
        sheet.merge_cells(start_column=col+1,start_row=1,end_column=col+1,end_row=3)
        sheet.cell(row=1,column=col+1).alignment = xl.styles.Alignment(horizontal='center')

    sheet.column_dimensions['A'].width = 50

    qp_cols = {}
    seq_rows = {}
    res_ref = {}

    # Write stat row
    for (qp,item) in sorted(tuple(data.values())[0].items()):
        sheet.cell(row=2,column=sheet.max_column+1).value = __R_KBS
        sheet.merge_cells(start_column=sheet.max_column,start_row=2,end_column=sheet.max_column,end_row=3)
        sheet.cell(row=2,column=sheet.max_column).alignment = xl.styles.Alignment(horizontal='center')

        for val in __R_PSNR_SUB:
            sheet.cell(row=3,column=sheet.max_column+1).value = val
        sheet.cell(row=2,column=sheet.max_column-len(__R_PSNR_SUB)+1).value = __R_PSNR
        sheet.merge_cells(start_column=sheet.max_column-len(__R_PSNR_SUB)+1,start_row=2,end_column=sheet.max_column,end_row=2)
        sheet.cell(row=2,column=sheet.max_column-len(__R_PSNR_SUB)+1).alignment = xl.styles.Alignment(horizontal='center')
        
        qp_cols[qp] = sheet.max_column-len(__R_PSNR_SUB)
        sheet.cell(row=1,column=qp_cols[qp]).value = __R_HEADER_QP.format(qp)
        sheet.merge_cells(start_column=qp_cols[qp],start_row=1,end_column=sheet.max_column,end_row=1)
        sheet.cell(row=1,column=qp_cols[qp]).alignment = xl.styles.Alignment(horizontal='center')

    # Write sequence column
    for (seq,res) in data.items():
        sheet.cell(row=sheet.max_row+1,column=1).value = __SEQ_FORMAT.format(seq,scale)
        seq_rows[seq] = sheet.max_row

        res_ref[seq] = {}
            
        #Set Layers
        sheet.cell(row=seq_rows[seq],column=2).value = __LID_TOT
        res_ref[seq][__LID_TOT] = {__KBS:[],__PSNR:[]}
        for lid in range(len(tuple(res.values())[0].keys())-1):
            sheet.cell(row=seq_rows[seq]+lid+1,column=2).value = lid
            res_ref[seq][lid] = {__KBS:[],__PSNR:[]}
        

    # Write Average "sequence"
    sheet.cell(row=sheet.max_row+1,column=1).value = __SEQ_AVERAGE
    seq_rows[__SEQ_AVERAGE] = sheet.max_row

    res_ref[__SEQ_AVERAGE] = {}
            
    #Set Layers
    sheet.cell(row=seq_rows[__SEQ_AVERAGE],column=2).value = __LID_TOT
    res_ref[__SEQ_AVERAGE][__LID_TOT] = {__KBS:[],__PSNR:[]}
    for lid in range(len(tuple(res.values())[0].keys())-1):
        sheet.cell(row=seq_rows[__SEQ_AVERAGE]+lid+1,column=2).value = lid
        res_ref[__SEQ_AVERAGE][lid] = {__KBS:[],__PSNR:[]}
    

    # Set actual data
    for (seq,qps) in data.items():
        for (qp,item) in sorted(tuple(qps.items())):
            for (lid,val) in item.items():
                r = seq_rows[seq] + lid + 1
                if lid == __LID_TOT:
                    r = seq_rows[seq]
                c_kbs = qp_cols[qp]
                c_psnr = c_kbs + len(__R_PSNR_SUB)

                sheet.cell(row=r,column=c_kbs).value = val[__KBS]

                for i in range(len(__R_PSNR_SUB)-1):
                    sheet.cell(row=r,column=c_psnr-i-1).value = float(val[__PSNR][-i-1])
                sheet.cell(row=r,column=c_psnr).value = __PSNR_AVG.format(y = get_column_letter(c_psnr-3) + str(r),
                                                                          u = get_column_letter(c_psnr-2) + str(r),
                                                                          v = get_column_letter(c_psnr-1) + str(r))

                res_ref[seq][lid][__KBS].append(get_column_letter(c_kbs) + str(r))
                res_ref[seq][lid][__PSNR].append(get_column_letter(c_psnr) + str(r))
    
    # Set Average data
    for c_kbs in sorted(qp_cols.values()):
        for lid in res_ref[__SEQ_AVERAGE]:
            r = seq_rows[__SEQ_AVERAGE] + lid + 1
            if lid == __LID_TOT:
                r = seq_rows[__SEQ_AVERAGE]
            #c_kbs = qp_cols[qp]
            c_psnr = c_kbs + len(__R_PSNR_SUB)

            kbs_rows = []
            for (seq,row) in seq_rows.items():
                if seq == __SEQ_AVERAGE:
                    continue
                kbs_rows.append(get_column_letter(c_kbs)+str(row+lid+1))
            sheet.cell(row=r,column=c_kbs).value = __C_AVG.format(','.join(kbs_rows))

            for i in range(len(__R_PSNR_SUB)-1):
                psnr_rows = []
                for (seq,row) in seq_rows.items():
                    if seq == __SEQ_AVERAGE:
                        continue
                    psnr_rows.append(get_column_letter(c_psnr-i-1)+str(row+lid+1))
                sheet.cell(row=r,column=c_psnr-i-1).value = __C_AVG.format(','.join(psnr_rows))
            
            sheet.cell(row=r,column=c_psnr).value = __PSNR_AVG.format(y = get_column_letter(c_psnr-3) + str(r),
                                                                      u = get_column_letter(c_psnr-2) + str(r),
                                                                      v = get_column_letter(c_psnr-1) + str(r))

            res_ref[__SEQ_AVERAGE][lid][__KBS].append(get_column_letter(c_kbs) + str(r))
            res_ref[__SEQ_AVERAGE][lid][__PSNR].append(get_column_letter(c_psnr) + str(r))

    sheet.freeze_panes = 'A4'

    return res_ref


"""
Write results to workbook. Assume wb has a Summary and Result Sheet.
"""
def __writeResults(wb,results,layers={}):
    s_sheet = wb.get_sheet_by_name('Summary')
    res_pos = {}
    
    # Write test results
    for (test,res) in sorted(results.items()):
        n_sheet = wb.create_sheet(title=test,index=0)
        res_pos[test] = __writeSheet(n_sheet,res[__RES],res[__SCALE])
    res_pos = __makeSummary(res_pos,layers)
    #print(res_pos)
    #write summary sheet
    __writeSummary(s_sheet,res_pos)
    wb.active = wb.get_index(s_sheet)

"""
Run given tests and write results to a exel file
@param combi: Give a list of test names that are combined into one test
@param layers: A dict with test names as keys containing a list of layers to include in summary
"""
def runTests( tests, outname, combi = [], layers = {} ):
    print('Start running tests...')
    for test in tests:
        #print("Running test {}...".format(test._test_name))
        test.run()
    print('Tests complete.')
    print('Writing results to file {}...'.format(cfg.results + outname + __FILE_END))
    res = __parseTestResults(tests)
    res = __combiTestResults(res,combi)

    wb = xl.load_workbook(cfg.exel_template,keep_vba=True)
    __writeResults(wb,res,layers)
    wb.save(cfg.results + outname + __FILE_END)
    print('Done.')
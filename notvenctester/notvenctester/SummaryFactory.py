"""
Module for defining and processing summary sheets
"""

import openpyxl as xl

#Define summary names used as keys f in definitions
sn_BDBRM = "BDBRMatrix"

#Define definition templates for each summary type

"""
__LAYERS:{<LayerCombiName>:<tuple of layers to include>}
"""
__LAYERS = "layers"
__WRITE_BITS = "write_bits"
__WRITE_BDBR = "write_bdbr"
__WRITE_PSNR = "write_psrn"
__WRITE_TIME = "write_time"
dt_BDBRM = {__LAYERS:{}, __WRITE_BDBR: True, __WRITE_BITS: True, __WRITE_PSNR: True, __WRITE_TIME: True}

"""
for creating the BDBRMatrix definition
"""
def create_BDBRMatrix_definition(layers, write_bdbr, write_bits, write_psnr, write_time):
    definition = dt_BDBRM.copy()
    definition[__LAYERS] = layers
    definition[__WRITE_BDBR] = write_bdbr
    definition[__WRITE_BITS] = write_bits
    definition[__WRITE_PSNR] = write_psnr
    definition[__WRITE_TIME] = write_time
    return definition

"""
Function for creating summary sheets to the given workbook for the given data
@param wb: work book where sheets will be added
@param data_refs: references to the data sheets and data cell positions used for the summary in the form data_refs[<test_name>][<seq>][<lid>] = {__KB, __KBS,__PSNR, __TIME}
@param BDBRMatrix: dict containing the parameters for the BDBRMatrix summary type
"""
def makeSummaries(wb, data_refs, **definitions):
    if sn_BDBRM in definitions:
        makeBDBRMatrix(wb, data_refs, definitions[sn_BDBRM])


def makeBDBRMatrix(wb, data_refs, definition):
    bdbrm_sheet = wb.create_sheet(sn_BDBRM)
    reduced_refs = __makeSummary(data_refs, definitions[__LAYERS])
    __writeBDBRMatrix(bdbrm_sheet, reduced_refs, **definitions)


#######################################
# BDBRMatrix summary type definitions #
#######################################

__S_SEQ_HEADER = "Sequence {} results"
__S_BIT_HEADER = r"Bit comparisons"
__S_PSNR_HEADER = r"PSNR comparisons (dB)"
__S_TIME_HEADER = r"Encoding time comparisons"
__S_BDRATE_FORMAT = "=bdrate({},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})"
__S_BIT_FORMAT = "=AVERAGE({},{},{},{})/AVERAGE({},{},{},{})"
__S_TIME_FORMAT = "=AVERAGE({},{},{},{})/AVERAGE({},{},{},{})"
__S_PSNR_FORMAT = "=AVERAGE({},{},{},{})-AVERAGE({},{},{},{})"
__S_HEADER = "Result summary matrix (bdrate, bit, PSNR, Time comparisons)"


"""
Transform res_pos into summary test structure removing items not used in the summary
@return dict of the form res[<test_name>][<seq>] = {__KB, __KBS,__PSNR, __TIME}
"""
def __makeSummary(res_pos,layers={}):
    from TestSuite import _LID_TOT
    res = {}
    for (test,item) in res_pos.items():
        res[test] = {}
        for (seq,vals) in item.items():
            test_in_layers = test in layers
            if not test_in_layers:
                res[test][seq] = vals[LID_TOT]
                if len(vals.keys()) <= 2: #If only 2 lids, it should mean the total layer and other layer are the same
                    continue
            for (lid,val) in vals.items():
                if lid == LID_TOT and not test_in_layers:
                    continue
                if test_in_layers and lid not in layers[test]:
                    continue
                nn = makeSheetLayer(test,lid)
                if lid == LID_TOT or len(vals.keys()) <= 2:
                    nn = test
                if nn in res:
                    res[nn][seq] = val
                else:
                    res[nn] = {seq:val}

    return res

"""
Handle writing the BDBRMatrix summary sheet
"""
def __writeBDBRMatrix(sheet, data_refs, *, write_bdbr, write_bits, write_psnr, write_time, **other):
    seq_ref = {}
    order = order if order else list(seq_ref.keys())

    # Init structure for each sequence
    for (test,item) in data_refs.items():
        for seq in item.keys():
            seq_ref[seq] = {}
    # Populate
    for (test,item) in data_refs.items():
        for (seq,val) in item.items():
            seq_ref[seq][test] = val
    #print(seq_ref)
    # For each sequence generate the comparison matrix
    sheet.cell(row = 1, column = 1).value = __S_HEADER 
    #for (seq,ref) in sorted(seq_ref.items()):
    for seq in order:
        ref = seq_ref[seq]
        tests = sorted(ref.keys())
        
        row = sheet.max_row + 2
        brow = row
        prow = row
        trow = row
        col = 1 #sheet.max_column + 1
        
        # write bdrate matrix
        if write_bdbr:  

            sheet.cell(row = row, column = col).value = __S_SEQ_HEADER.format(seq)
            sheet.merge_cells(start_column=col,start_row=row,end_column=col+len(tests),end_row=row)
            (row, col) = __writeSummaryMatrixHeader(sheet, tests, row+1, col)
            __writeBDSummaryMatrix(sheet, ref, row, col)

        # write bit matrix
        if write_bits:
            if 'bcol' not in locals():
                bcol = sheet.max_column + 2
            sheet.cell(row = brow, column = bcol).value = __S_BIT_HEADER
            sheet.merge_cells(start_column=bcol,start_row=brow,end_column=bcol+len(tests),end_row=brow)
            (brow, col) = __writeSummaryMatrixHeader(sheet, tests, brow+1, bcol)
            __writeBSummaryMatrix(sheet, ref, brow, col)

        # write psnr matrix
        if write_psnr:
            if 'pcol' not in locals():
                pcol = sheet.max_column + 2
            sheet.cell(row = prow, column = pcol).value = __S_PSNR_HEADER
            sheet.merge_cells(start_column=pcol,start_row=prow,end_column=pcol+len(tests),end_row=prow)
            (prow, col) = __writeSummaryMatrixHeader(sheet, tests, prow+1, pcol)
            __writePSNRSummaryMatrix(sheet, ref, prow, col)

        # write time matrix
        if write_time:
            if 'tcol' not in locals():
                tcol = sheet.max_column + 2
            sheet.cell(row = trow, column = tcol).value = __S_TIME_HEADER
            sheet.merge_cells(start_column=tcol,start_row=trow,end_column=tcol+len(tests),end_row=trow)
            (trow, col) = __writeSummaryMatrixHeader(sheet, tests, trow+1, tcol)
            __writeTimeSummaryMatrix(sheet, ref, trow, col)

    # Make columns wider
    for col in range(sheet.max_column):
        sheet.column_dimensions[get_column_letter(col+1)].width = getMaxLength(list(data_refs.keys()))


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
Write summary matrix data for bdrate
"""
def __writeBDSummaryMatrix(sheet, data, row, col):
    from TestSuite import _PSNR
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
                r1 =[__SR_FORMAT.format(sheet=parseSheetLayer(t1)[0],cell=cl) for cl in data[t1][_KBS] + data[t1][_PSNR]]
                r2 =[__SR_FORMAT.format(sheet=parseSheetLayer(t2)[0],cell=cl) for cl in data[t2][_KBS] + data[t2][_PSNR]]
                sheet.cell(row = r, column = c).value = __S_BDRATE_FORMAT.format(*(r1+r2))
                sheet.cell(row = r, column = c).style = 'Percent'
                sheet.cell(row = r, column = c).number_format = '0.00%'
            sheet.cell(row=r,column=c).alignment = xl.styles.Alignment(horizontal='center')
    # Set conditional coloring
    form_range = "{}:{}".format(get_column_letter(col)+str(row),get_column_letter(final_c)+str(final_r))
    sheet.conditional_formatting.add(form_range,
                                     ColorScaleRule(start_type='percentile', start_value=90, start_color='63BE7B',
                                                    mid_type='num', mid_value=0, mid_color='FFFFFF',
                                                    end_type='percentile', end_value=10, end_color='F8696B' ))


"""
Write bit size summary matrix
"""
def __writeBSummaryMatrix(sheet, data, row, col):
    from TestSuite import _KB
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
                r2 =[__SR_FORMAT.format(sheet=parseSheetLayer(t1)[0],cell=cl) for cl in data[t1][_KB]]
                r1 =[__SR_FORMAT.format(sheet=parseSheetLayer(t2)[0],cell=cl) for cl in data[t2][_KB]]
                sheet.cell(row = r, column = c).value = __S_BIT_FORMAT.format(*(r1+r2))
                sheet.cell(row = r, column = c).style = 'Percent'
            sheet.cell(row=r,column=c).alignment = xl.styles.Alignment(horizontal='center')
    # Set conditional coloring
    form_range = "{}:{}".format(get_column_letter(col)+str(row),get_column_letter(final_c)+str(final_r))
    sheet.conditional_formatting.add(form_range,
                                     ColorScaleRule(start_type='min', start_color='4F81BD',
                                                    mid_type='num', mid_value=1, mid_color='FFFFFF',
                                                    end_type='percentile', end_value=80, end_color='F8696B' ))

"""
Write time summary matrix
"""
def __writeTimeSummaryMatrix(sheet, data, row, col):
    from TestSuite import _TIME
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
                r2 =[__SR_FORMAT.format(sheet=parseSheetLayer(t1)[0],cell=cl) for cl in data[t1][_TIME]]
                r1 =[__SR_FORMAT.format(sheet=parseSheetLayer(t2)[0],cell=cl) for cl in data[t2][_TIME]]
                sheet.cell(row = r, column = c).value = __S_TIME_FORMAT.format(*(r1+r2))
                sheet.cell(row = r, column = c).style = 'Percent'
            sheet.cell(row=r,column=c).alignment = xl.styles.Alignment(horizontal='center')
    # Set conditional coloring
    form_range = "{}:{}".format(get_column_letter(col)+str(row),get_column_letter(final_c)+str(final_r))
    sheet.conditional_formatting.add(form_range,
                                     ColorScaleRule(start_type='min', start_color='9BDE55',#'63BE7B',
                                                    mid_type='num', mid_value=1, mid_color='FFFFFF',
                                                    end_type='percentile', end_value=80, end_color='00BBEF'))#'4F81BD' ))

"""
Write psnr summary matrix
"""
def __writePSNRSummaryMatrix(sheet, data, row, col):
    from TestSuite import _PSNR
    test_col = col - 1
    test_row = row - 1
    final_r = row+len(data.keys())
    final_c = col+len(data.keys())
    for r in range(row,row+len(data.keys())):
        for c in range(col,col+len(data.keys())):
            t2 = sheet.cell(row = r, column = test_col).value
            t1 = sheet.cell(row = test_row, column = c).value
            if t1 == t2:
                sheet.cell(row = r, column = c).value = 0#"-"
            else:
                r2 =[__SR_FORMAT.format(sheet=parseSheetLayer(t1)[0],cell=cl) for cl in data[t1][_PSNR]]
                r1 =[__SR_FORMAT.format(sheet=parseSheetLayer(t2)[0],cell=cl) for cl in data[t2][_PSNR]]
                sheet.cell(row = r, column = c).value = __S_PSNR_FORMAT.format(*(r1+r2))
            sheet.cell(row = r, column = c).style = 'Comma'
            sheet.cell(row=r,column=c).alignment = xl.styles.Alignment(horizontal='center')
    # Set conditional coloring
    form_range = "{}:{}".format(get_column_letter(col)+str(row),get_column_letter(final_c)+str(final_r))
    sheet.conditional_formatting.add(form_range,
                                     ColorScaleRule(start_type='min', start_color='FF772A',
                                                    mid_type='num', mid_value=0, mid_color='FFFFFF',
                                                    end_type='max', end_color='9BDE55' ))
import pandas as pd
import numpy as np

def cheques_inwards(ripps_clean,ledger):
    cheque_ripps = ripps_clean[ripps_clean['Type']=='pacs.003. 001.08']
    cheque_ripps = cheque_ripps[cheque_ripps['Debit Account'].str.contains('1240100').fillna(False)]
    cheque_ripps=cheque_ripps[(cheque_ripps.Status !="transaction is rejected due to error")]

    single_bulk_All=cheque_ripps[(~cheque_ripps['Batch_no'].is_unique)&(cheque_ripps['Reference_new'].isnull())]
    print('batchsss',single_bulk_All.shape)
    # clean_df = cheque_ripps[(~single_bulk)]
    cheque_ripps = cheque_ripps[~(cheque_ripps['Reference'].isin(single_bulk_All['Reference']))]


    rec_id = ledger.RECID.str.split(';', expand=True, n=1)
    ledger['legder_recid'] = rec_id[0]
    ledger = ledger[ledger['CREDIT_ACCT_NO']=='RWF1701400021002']
    instnID = ledger['API_UNIQUE_ID'].str.slice(start=8)
    # instnID
    ledger['instnID'] = instnID

    cheque_ripps['Reference']= cheque_ripps['Reference'].astype(str)
    ledger['instnID'] = ledger['instnID'].astype(str)

    _merge_cheque_0808 = pd.merge(cheque_ripps,ledger, how='right',left_on='Reference',right_on='instnID',)
    print(' side',_merge_cheque_0808.shape)
    ripps_merge_cheque_0808 = pd.merge(cheque_ripps,ledger, how='left',left_on='Reference',right_on='instnID',)
    print('ripps side ',ripps_merge_cheque_0808.shape)

    cheque_matching = _merge_cheque_0808[_merge_cheque_0808['Reference'] == _merge_cheque_0808['instnID']]
    print(cheque_matching.shape)
    legder_cheque_mismatch = _merge_cheque_0808[_merge_cheque_0808['Reference'] != _merge_cheque_0808['instnID']]
    print(legder_cheque_mismatch.shape)
    ripps_cheque_mismatch = ripps_merge_cheque_0808[ripps_merge_cheque_0808['Reference'] != ripps_merge_cheque_0808['instnID']]
    print(ripps_cheque_mismatch.shape)
    
    
    return cheque_matching , legder_cheque_mismatch , ripps_cheque_mismatch

def outward(Stmnt,Ripps):
    Ripps = Ripps[Ripps['Credit Account '].str.contains('1240100').fillna(False)] 
    ripps = Ripps[Ripps['Type'] == 'pacs.003. 001.08']
    BNR_merge = pd.merge(Stmnt,ripps, how='right',left_on='NAreference', right_on='Breference')
    _merge = pd.merge(Stmnt,ripps, how='left', left_on='NAreference', right_on='Breference')
    match_bnr = BNR_merge[(BNR_merge['NAreference']==BNR_merge['Breference']) | (BNR_merge['NAreference']==BNR_merge['Nreference'])]
    mismatch_bnr = BNR_merge[(BNR_merge['NAreference']!=BNR_merge['Breference']) ]
    mismatch_ = _merge[(_merge['NAreference']!=_merge['Breference'])  ]
    print('BNR merged:',BNR_merge.shape)
    print(' merged:' ,_merge.shape)
    print('matched:' ,match_bnr.shape)
    print('BNR mismatch:' ,mismatch_bnr.shape)
    print(' mismatch:' ,mismatch_.shape)
    return match_bnr,mismatch_bnr,mismatch_

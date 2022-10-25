import pandas as pd
import numpy as np

def withdraws( bnr_ripps,_ledger_df):

#     withdraws on bnr ripps
    withdraws_ripps = bnr_ripps[bnr_ripps['Debit Account'].str.contains('1240100').fillna(False)]
    withdraws_ripps = withdraws_ripps[withdraws_ripps['Type']=='pacs.009. 001.08']
    withdraws_ripps = withdraws_ripps[withdraws_ripps['Reference'].str.startswith('FT').fillna(False)]
    # withdraws_ripps = withdraws_ripps[withdraws_ripps['Remittance infos'].str.contains('PTR/002').fillna(False)]
    print('withdraws ripps',withdraws_ripps.shape)
    
#     withdraws on  ledger 
    _ledger = _ledger_df[_ledger_df['DEBIT_ACCT_NO']=='RWF1701400901002']
    _ledger = _ledger[_ledger['PAYMENT_DETAILS'].str.contains('TT').fillna(False)]
    _ledger = _ledger[_ledger['PAYMENT_DETAILS'].str.contains('FT').fillna(False)]
    print('withdraws  ledger',withdraws_ripps.shape, 'withdraws ledger', _ledger.shape)
    
#     Maching  bnr combined 
    rec_id = _ledger.PAYMENT_DETAILS.str.split(' ', expand=True, n=1)
    _ledger['log_recid'] = rec_id[1]
    
    merge_bnr_ = pd.merge(withdraws_ripps, _ledger, how='outer',left_on='Reference',right_on='log_recid',)
    print('withdraws merged both sides ',merge_bnr_.shape)
    
    withdraws_matching = merge_bnr_[merge_bnr_['Reference'] == merge_bnr_['log_recid']]
    print('withdraws matching', withdraws_matching.shape)
    withdraws_matching.to_excel('july_withdraws_matching.xlsx')

#     mismatch on bnr side 
    merge_bnr_ripps = pd.merge(withdraws_ripps, _ledger, how='left',left_on='Reference',right_on='log_recid',)
    print('withdraws merged on bnr ripps ',merge_bnr_ripps.shape)
    
    withdraws_mismatching_bnr_ripps = merge_bnr_ripps[merge_bnr_ripps['Reference'] != merge_bnr_ripps['log_recid']]
    print('withdraws mismatch on bnr ripps ', withdraws_mismatching_bnr_ripps.shape)
    withdraws_mismatching_bnr_ripps.to_excel('july_withdraws_bnr_mismatching.xlsx')

    #     mismatch on  side 
    merge__ledger = pd.merge(withdraws_ripps, _ledger, how='right',left_on='Reference',right_on='log_recid',)
    print('withdraws merged on  ledger ',merge__ledger.shape)
    
    withdraws_mismatching__ledger = merge__ledger[merge__ledger['Reference'] != merge__ledger['log_recid']]
    print('withdraws mismatch on  ledger ', withdraws_mismatching__ledger.shape)
    withdraws_mismatching__ledger.to_excel('july_withdraws__mismatching.xlsx')

    return withdraws_matching,withdraws_mismatching__ledger, withdraws_mismatching_bnr_ripps

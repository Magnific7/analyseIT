import pandas as pd
import numpy as np

def deposit(bnr_ripps,_ledger_df):

#     deposit on bnr ripps
    deposit_ripps = bnr_ripps[bnr_ripps['Credit Account '].str.contains('1240100').fillna(False)]
    deposit_ripps = deposit_ripps[deposit_ripps['Type']=='pacs.009. 001.08']
    deposit_ripps = deposit_ripps[deposit_ripps['Reference'].str.startswith('FT').fillna(False)]
    deposit_ripps = deposit_ripps[deposit_ripps['Remittance infos'].str.contains('PTR/003').fillna(False)]
    print('deposit ripps',deposit_ripps.shape)
    
#     deposit on  ledger 
    _ledger = _ledger_df[_ledger_df['DEBIT_ACCT_NO']=='RWF1701400901002']
    _ledger = _ledger[_ledger['PAYMENT_DETAILS'].str.contains('TT').fillna(False)]
    _ledger = _ledger[_ledger['PAYMENT_DETAILS'].str.contains('FT').fillna(False)]
    print('deposit  ledger',deposit_ripps.shape, 'deposit ledger', _ledger.shape)
    
#     Maching  bnr combined 
    rec_id = _ledger.PAYMENT_DETAILS.str.split(' ', expand=True, n=1)
    _ledger['log_recid'] = rec_id[1]
    
    merge_bnr_ = pd.merge(deposit_ripps, _ledger, how='outer',left_on='Reference',right_on='log_recid',)
    print('deposit merged both sides ',merge_bnr_.shape)
    
    deposit_matching = merge_bnr_[merge_bnr_['Reference'] == merge_bnr_['log_recid']]
    print('deposit matching', deposit_matching.shape)
#     deposit_matching.to_excel('july_deposit_matching.xlsx')

#     mismatch on bnr side 
    merge_bnr_ripps = pd.merge(deposit_ripps, _ledger, how='left',left_on='Reference',right_on='log_recid',)
    print('deposit merged on bnr ripps ',merge_bnr_ripps.shape)
    
    deposit_mismatching_bnr_ripps = merge_bnr_ripps[merge_bnr_ripps['Reference'] != merge_bnr_ripps['log_recid']]
    print('deposit mismatch on bnr ripps ', deposit_mismatching_bnr_ripps.shape)
#     deposit_mismatching_bnr_ripps.to_excel('july_deposit_bnr_mismatching.xlsx')

    #     mismatch on  side 
    merge__ledger = pd.merge(deposit_ripps, _ledger, how='right',left_on='Reference',right_on='log_recid',)
    print('deposit merged on  ledger ',merge__ledger.shape)
    
    deposit_mismatching__ledger = merge__ledger[merge__ledger['Reference'] != merge__ledger['log_recid']]
    print('deposit mismatch on  ledger ', deposit_mismatching__ledger.shape)
#     deposit_mismatching__ledger.to_excel('july_deposit__mismatching.xlsx')

    return deposit_matching,deposit_mismatching__ledger,deposit_mismatching_bnr_ripps

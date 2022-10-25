import pandas as pd
import numpy as np
from .. import views

def mis_match_in_updated_new( bnr,):
    bnr = bnr[bnr['Credit Account '].str.contains('1240100').fillna(False)]
    bnr = bnr[bnr['Type']=='pacs.008. 001.08']
    _ledger = [['DEBIT_ACCT_NO']=='RWF1701400041002'] 

#     _ledger.reset_index(level=0, inplace=True)
    _ledger['new'] = _ledger[_ledger['TRANSACTION_TYPE']=='ACLJ']['PAYMENT_DETAILS']

#     _ledger['new'].value_counts()
    df = _ledger['new'].str.split(' ', expand=True, n=1)
    _ledger['new'] = df[0]
    _ledger.loc[_ledger['new'].notna(),'DEBIT_THEIR_REF']=_ledger['new']
#     _ledger.loc[_ledger['DEBIT_THEIR_REF'].isnull(),'DEBIT_THEIR_REF']= _ledger['API_UNIQUE_ID']
    
    
    bnr.Amount = bnr.Amount.astype(str).str.replace(',', '')
    bnr.Amount = pd.to_numeric(bnr.Amount, errors='coerce')

    _ledger.LOC_AMT_DEBITED = pd.to_numeric(_ledger.LOC_AMT_DEBITED, errors='coerce')

##############################################insert '-' on DEBIT_THEIR_REF to make it similar to BNR Reference########################################
    string_ref = _ledger[(_ledger['TRANSACTION_TYPE']=='ACLJ')&(_ledger['new'].notna())
             &(_ledger['DEBIT_THEIR_REF'].str.startswith('FT'))]['DEBIT_THEIR_REF'] 

    _ledger.loc[(_ledger['TRANSACTION_TYPE']=='ACLJ')&(_ledger['new'].notna())
         &(_ledger['DEBIT_THEIR_REF'].str.startswith('FT')), 'DEBIT_THEIR_REF'] = string_ref.str.slice(stop=12)+ '-'+ string_ref.str[12:]
       
##########################Converting reference with digit to numeric format ##################################   
    _ledger.loc[_ledger['DEBIT_THEIR_REF'].str.isdigit().fillna(False), 'DEBIT_THEIR_REF']= pd.to_numeric(_ledger[_ledger['DEBIT_THEIR_REF'].str.isdigit().fillna(False)]['DEBIT_THEIR_REF'],downcast ='signed').fillna(False)
    bnr.loc[bnr['Reference'].str.isdigit().fillna(False),'Reference']=pd.to_numeric(bnr[bnr['Reference'].str.isdigit().fillna(False)]['Reference'],downcast ='signed').fillna(False)
##########################################################################################################################
#############################################Merging FT references########################################################    
    _ledger.loc[(_ledger['new'].notna())&
                    (_ledger['DEBIT_THEIR_REF'].str.startswith('FT').fillna(False))&
                  (_ledger['DEBIT_THEIR_REF'].str.endswith('-').fillna(False)), 'DEBIT_THEIR_REF']= _ledger[(_ledger['new'].notna())&
                    (_ledger['DEBIT_THEIR_REF'].str.startswith('FT').fillna(False))&
                  (_ledger['DEBIT_THEIR_REF'].str.endswith('-').fillna(False))]['new']

    single_tr =bnr[bnr['Credit Account ']=='1240100-RWF\n(IGRWRW)']

    #####################Bulk details#####################################################################

    bulk_tr_det = bnr[(bnr['Credit Account ']=='1240100-RWF-CL-CR\n(IGRWRW)')
                                &(bnr['Reference_new'].notna())]

    ####################Single bulk transfer##########################################################

    single_bulk=bnr[(bnr['Batch_no'].is_unique)&bnr['Reference_new'].isnull()&(bnr['Credit Account ']=='1240100-RWF-CL-CR\n(IGRWRW)')]


    bnr_cleaned = pd.concat([single_tr,bulk_tr_det,single_bulk],axis=0, ignore_index=True)
    ####################################################################################################
    Rejected = bnr_cleaned[(bnr_cleaned['Debit Account'].str.contains('1240100').fillna(False))|
                                     (bnr_cleaned['Status'].str.contains('rejected').fillna(False))]
    #####Removing rejected transactions##########################
    bnr_cleaned_new = bnr_cleaned[~(bnr_cleaned['Debit Account'].str.contains('1240100').fillna(False))&
                                     ~(bnr_cleaned['Status'].str.contains('rejected').fillna(False))]
    ####################################################################################################

    bnr_cleaned_new['Datenum'] = pd.to_datetime(bnr_cleaned_new['Value Date'],dayfirst=True)
    bnr_cleaned_new['Datenum'] = bnr_cleaned_new['Datenum'].dt.strftime('%Y%m%d')
    bnr_cleaned_new['Datenum'] = pd.to_numeric(bnr_cleaned_new['Datenum'].astype(int))
    
    _ledger['DEBIT_VALUE_DATE'] =pd.to_numeric(_ledger['DEBIT_VALUE_DATE'].astype(int))
    ###################################################################################################
    print('Input data size :{}, bnr:{}'.format(_ledger.shape,  bnr_cleaned_new.shape))


########################################################################Preparation of ripps#####################

    bnr_cleaned_new1 = bnr_cleaned_new[~bnr_cleaned_new['Batch_no'].str.startswith('FT').fillna(False)&
           (bnr_cleaned_new['Reference'].duplicated())&(bnr_cleaned_new['Reference_new'].isnull()
                                                            &~(bnr_cleaned_new['Reference'].astype(str).str.startswith('220')))]

    bnr_cleaned_new2 = bnr_cleaned_new[bnr_cleaned_new['Batch_no'].str.startswith('FT').fillna(False)
                   &bnr_cleaned_new['Reference'].duplicated()&(bnr_cleaned_new['Reference_new'].isnull())]
    
    bnr_cleaned_new3 = pd.concat([bnr_cleaned_new1,bnr_cleaned_new2], axis=0, ignore_index=True)
    bnr_cleaned_new3_new = bnr_cleaned_new3.drop_duplicates('Reference', keep='first')###drop duplicates where ledger appears once

    bnr_data = bnr_cleaned_new.copy()
    print('bnr data after removing duplicates',bnr_data.shape)
 ####################################################################################################   
    Final_merge_= pd.merge(_ledger, bnr_data, how='left', left_on='DEBIT_THEIR_REF', right_on='Reference')

#     Final_merge_ = Final_merge_.drop_duplicates(subset='RECID', keep='last')

    print('Merged data on  side',Final_merge_.shape)

      
    Final_merge_bnr= pd.merge(_ledger, bnr_data, how='right',left_on='DEBIT_THEIR_REF', right_on='Reference')


    Final_merge_bnr_new =Final_merge_bnr.copy()

    print('Merged data on BNR side',Final_merge_bnr_new.shape)
    
    
    ############################################################################################################################
#     Final_merge_['Days_diff'] = (pd.to_datetime(Final_merge_['Date'])-pd.to_datetime(Final_merge_['Value Date'])).dt.days
    Final_merge_['Date_diff'] = Final_merge_['DEBIT_VALUE_DATE']-Final_merge_['Datenum']
    Final_merge_bnr_new['Date_diff'] = Final_merge_bnr_new['DEBIT_VALUE_DATE']-Final_merge_bnr_new['Datenum']

    
    match_1 = Final_merge_[(Final_merge_['RECID'].notna())
                              &(Final_merge_['DEBIT_THEIR_REF'] ==Final_merge_['Reference'])
                              &(Final_merge_['Amount']==Final_merge_['LOC_AMT_DEBITED'])
#                                &(Final_merge_['Date_diff']>=0)
                              ]

    match_bnr1= Final_merge_bnr_new[(Final_merge_bnr_new['RECID'].notna())
                              &(Final_merge_bnr_new['DEBIT_THEIR_REF'] ==Final_merge_bnr_new['Reference'])
                              &(Final_merge_bnr_new['Amount']==Final_merge_bnr_new['LOC_AMT_DEBITED'])
#                                    &(Final_merge_bnr_new['Date_diff']>=0)
                                   ]
####################################Handling the duplicates on  side and on bnr side#######################    
    pos =match_1[match_1['Date_diff']>=0].sort_values('Date_diff').drop_duplicates('RECID')
    match__final =pos
    
    neg =match_1[match_1['Date_diff']<0].sort_values('Date_diff', ascending=False).drop_duplicates('RECID')
    neg_new =neg[~neg['RECID'].isin(pos['RECID'])]

    mismatch__new1 = Final_merge_[Final_merge_['Reference'].isnull()]
    mismatch__new2 = Final_merge_[Final_merge_['Reference'].notna()&
                                            (Final_merge_['Reference']==Final_merge_['DEBIT_THEIR_REF'])&
                                (Final_merge_['Amount']!=Final_merge_['LOC_AMT_DEBITED'])
#                                      &(Final_merge_['Date_diff']>=0)
                                     ]
    
    mismatch__new = pd.concat([mismatch__new1,mismatch__new2], axis=0, ignore_index=True)

    mis = mismatch__new[~mismatch__new['RECID'].isin(match__final['RECID'])]
#     mismatch__up_new1 =mismatch__up_new[~mismatch__up_new['RECID'].isin(match_up_new['RECID'])]

#     mismatch__final = pd.concat([mis,neg_new],axis=0,ignore_index=True)
    mismatch__final=mis
    mismatch_bnr_new1 = Final_merge_bnr_new[Final_merge_bnr_new['RECID'].isnull()]
    mismatch_bnr_new2 = Final_merge_bnr_new[Final_merge_bnr_new['RECID'].notna()&
                                            (Final_merge_bnr_new['Reference']==Final_merge_bnr_new['DEBIT_THEIR_REF'])&
                                (Final_merge_bnr_new['Amount']!=Final_merge_bnr_new['LOC_AMT_DEBITED'])
#                                            &(Final_merge_bnr_new['Date_diff']>=0)
                                           ]
    mismatch_bnr_new3 =bnr_cleaned_new3.drop_duplicates('Reference', keep='last') 
    mismatch_bnr_new = pd.concat([mismatch_bnr_new1,mismatch_bnr_new2], axis=0, ignore_index=True)
    
    pos_bnr = match_bnr1[match_bnr1['Date_diff']>=0].sort_values('Date_diff').drop_duplicates('RECID')
    neg_bnr = match_bnr1[match_bnr1['Date_diff']<0].sort_values('Date_diff', ascending=False).drop_duplicates('RECID')
    neg_bnr_new =neg_bnr[~neg_bnr['RECID'].isin(pos_bnr['RECID'])]
    misbnr = mismatch_bnr_new[~mismatch_bnr_new['RECID'].isin(match_bnr1['RECID'])]

    0=pos_bnr[(pos_bnr['Reference_new'].notna())]
    1 = pos_bnr[(pos_bnr['Reference_new'].isnull())&(pos_bnr['Reference'].duplicated())]
    2 = pos_bnr[pos_bnr['Reference'].duplicated()&(pos_bnr['Reference_new'].notna())&(pos_bnr['Batch_no'].str.startswith('RT'))]
    # 3 =pos_bnr[(pos_bnr['Batch_no']=='T133008924020627')]
    _duplicates = pd.concat([1,2],axis=0, ignore_index=True)

    new =_duplicates.sort_values('Date_diff').drop_duplicates('RECID').drop_duplicates('Reference')
    7 = 0[~0['Reference'].duplicated()]
    8 =0[0['Reference'].duplicated()&~0['Batch_no'].str.startswith('RT')]
    # 9 =0[0['Reference'].duplicated()&0['Batch_no'].str.startswith('RT')]

    3 =pos_bnr[(pos_bnr['Reference_new'].isnull())]
    3 =3[~3['Reference'].duplicated()]
    match_bnr_final = pd.concat([7+8+3+new], axis=0, ignore_index=True)
    mismatch_bnr_final = pd.concat([neg_bnr_new,misbnr], axis=0, ignore_index=True)


    print('Matched data on  side:\n', match__final.shape)
    print('Mismatched data on  side:\n', mismatch__final.shape)
    print('Mismatched data on bnr side:\n', mismatch_bnr_final.shape)
    

    return match__final, mismatch__final, mismatch_bnr_final 

def mis_match_out(bnr,):

    bnr = bnr[bnr['Debit Account'].str.contains('1240100').fillna(False)]
    bnr = bnr[bnr['Type']=='pacs.008. 001.08']
    df = .RECID.str.split(';', expand=True, n=1)
    ['Reference_rip'] = df[0]
    _ledger = [['CREDIT_ACCT_NO']=='RWF1701400801002']  
    print('Input data size:{}'.format((bnr.shape, bnr.shape, _ledger.shape)))


#     onepart_merge = pd.merge(_ledger,bnr1, how='left', left_on='Reference_rip', right_on='Reference')
    Final_merge_= pd.merge(_ledger, bnr, how='left',left_on='Reference_rip', right_on='Reference')
    print('Merged data on  side',Final_merge_.shape)
    
    Final_merge_bnr= pd.merge(_ledger, bnr, how='right',left_on='Reference_rip', right_on='Reference')
    print('Merged data on BNR side',Final_merge_bnr.shape)
    
    match_ =Final_merge_[(Final_merge_['Reference_rip']==Final_merge_['Reference'])]

    
    mismatch_ = Final_merge_[(Final_merge_['Reference_rip']!=Final_merge_['Reference'])]
#                                          &(Final_merge_['DEBIT_THEIR_REF']!=Final_merge_['Batch_no'])]
    
    match_bnr = Final_merge_bnr[(Final_merge_bnr['Reference_rip']==Final_merge_bnr['Reference'])]
#                                           |(Final_merge_bnr['DEBIT_THEIR_REF']==Final_merge_bnr['Batch_no'])]
    
    mismatch_bnr =  Final_merge_bnr[(Final_merge_bnr['Reference_rip']!=Final_merge_bnr['Reference'])]
#                                          &(Final_merge_bnr['DEBIT_THEIR_REF']!=Final_merge_bnr['Batch_no'])]

    
    print('Matched data on  side:\n', match_.shape)
    print('Mismatched data on  side:\n', mismatch_.shape)
    
    print('Matched data on bnr side:\n', match_bnr.shape)
    print('Mismatched data on bnr side:', mismatch_bnr.shape)   

    return match_, mismatch_, mismatch_bnr

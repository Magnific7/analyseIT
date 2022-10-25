import pandas as pd
import numpy as np
import glob
import json
import re

def process_ripps(path):
    Ripp = pd.read_excel(path,sheet_name = None)
    Ripps=pd.concat(Ripp, ignore_index=True)
    Ripps = Ripps.iloc[14:]
    Ripps = Ripps.loc[:,~Ripps.columns.str.contains('transactions')]
    Ripps.columns=['Reference','Unnamed: 1','Unnamed: 2', 'Unnamed: 3','Value Date','Type','Debit Account','Unnamed: 7','Ordering Customer/Drawer',
                      'Unnamed: 9','Unnamed: 10','Credit Account ','Beneficiary','Remittance infos','Amount','Input Time',
                      'Unnamed: 16','Status', 'Modification Time','Unnamed: 19']
    Ripps = Ripps[1:]
    Ripps = Ripps.reset_index(drop=True)
    Ripps = Ripps.loc[:, Ripps.columns.notna()]
    Ripps = Ripps.dropna(subset=['Value Date'])
    
    return Ripps

def cleanbnr_data(data):

    # data.dropna(subset='Value Date', inplace=True)
    data= data.loc[~data.index.duplicated(), :]
    data.insert(1,'Reference_new', data[~data['Value Date'].astype(str).str.contains('-2022')]['Value Date'])
    data.rename(columns={'Reference':'Batch_no'}, inplace=True)
    data.insert(1,'Reference', data['Batch_no'])
    data.loc[~data['Value Date'].str.contains('-2022'),'Reference']=data[~data['Value Date'].astype(str).str.contains('-2022')]['Value Date']
    data.loc[data['Batch_no'].notna(),'Reference']=data['Batch_no']
    data.rename(columns={'Unnamed: 7':'Debit_acc_ind','Unnamed: 9':'Credit_acc_ind', 'Unnamed: 10':'Ordering_cust_ind', 'Unnamed: 19':'Rejected',
                             'Unnamed: 16':'Remittance_info_ind'},
                    inplace=True)
    data.loc[data['Reference_new'].notna(),'Credit_acc_ind']=data['Remittance infos']
    data.loc[data['Reference_new'].notna(),'Remittance infos']=np.NaN
    data.loc[data['Reference_new'].notna(),'Beneficiary']=data['Amount']
    data.loc[data['Reference_new'].notna(),'Amount']=data['Modification Time']

    data['Batch_no'].fillna(method='ffill',inplace=True)
    data['Type'].fillna(method='ffill',inplace=True)
    data['Credit Account '].fillna(method='ffill',inplace=True)
    data['Debit Account'].fillna(method='ffill',inplace=True)
    data['Ordering Customer/Drawer'].fillna(method='ffill',inplace=True)
    data['Remittance infos'].fillna(method='ffill',inplace=True)
    # bnr_14Jul_copy['Remittance_info_ind'].fillna(method='ffill',inplace=True)
    data['Status'].fillna(method='ffill',inplace=True)
    data['Modification Time'].fillna(method='ffill',inplace=True)
    data['Input Time'].fillna(method='ffill',inplace=True)
    data.loc[~data['Value Date'].astype(str).str.contains('-2022'),'Value Date']=np.NaN
    data['Value Date'].fillna(method='ffill',inplace=True)
    
    
    return data

def open_logs(path):
    log_data = open(path, 'r')
    result = {}
    i=0
    for line in log_data:
        data = {}
        columns =  line.split('|')
        data=columns
        result[i]=data
        i+=1
    json_file = json.dumps(result)
    logs_df = pd.read_json(json_file, orient='index')
    logs_df.columns = logs_df.iloc[0]
    logs_df = logs_df[1:]
    print("ledger_df>>>",logs_df.shape)
    return logs_df 


def clean_stmnt(Stmnt_path):
    Stmnt=pd.read_csv(Stmnt_path,header=7,skipinitialspace=True)
    Stmnt = Stmnt.dropna(subset=['Book Date','Description'])
    df5 =  [re.sub(r'[^a-zA-Z]', '', str(x)) for x in Stmnt["Narration"]]
    Stmnt['Names']=df5
    Stmnt.insert(9, 'NAreference', np.NaN)
    df2=Stmnt['Names'].str[:4]
    df3=Stmnt['Debit'].str[:4]
    Stmnt['NAreference']= df2.astype(str) +""+ df3
    Stmnt['NAreference']=Stmnt["NAreference"].str.replace(",","")
    Stmnt['NAreference']=Stmnt["NAreference"].str.replace(".","")
    Stmnt['NAreference']=Stmnt["NAreference"].str.replace(" ","")
    return Stmnt

def stmt_clean_ripps(Ripps):
    Ripps.insert(1, 'Batch_no', np.NaN)
    Ripps.insert(2, 'Reference_new', np.NaN)
    Ripps = Ripps.dropna(subset=['Modification Time'])
    Ripps.drop(Ripps[(Ripps['Debit Account'].str.contains('1240100').fillna(False)) & (Ripps['Credit Account '].str.contains('1240100').fillna(False))].index, inplace=True)
    Ripps['Status'] = Ripps['Status'].fillna('Active')
    Ripps.loc[~(Ripps['Value Date'].str.contains('-2022').fillna(False)),'Reference']= Ripps[~(Ripps['Value Date'].str.contains('-2022').fillna(False))]['Value Date']
    Ripps.loc[~(Ripps['Value Date'].str.contains('-2022').fillna(False)),'Value Date']= np.NaN
    Ripps["Input Time"] = Ripps["Input Time"].replace('Active', np.NaN)
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Beneficiary'] = Ripps['Amount']
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Amount'] = np.NaN
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Amount'] = Ripps['Modification Time']
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Modification Time'] = np.NaN
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Credit Account '] = Ripps['Remittance infos']
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Remittance infos'] = np.NaN
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Remittance infos'] = Ripps['Unnamed: 16']
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Unnamed: 16'] = np.NaN
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Ordering Customer/Drawer'] = Ripps['Unnamed: 10']
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Unnamed: 10'] = np.NaN
    Ripps.loc[~Ripps['Value Date'].str.contains('2022').fillna(False), 'Debit Account'] = Ripps['Unnamed: 7']
    Ripps.loc[~Ripps['Value Date'].str.contains('2020').fillna(False), 'Unnamed: 7'] = np.NaN
    Ripps = Ripps.loc[:,~Ripps.columns.str.contains('Unnamed')]
    Ripps.loc[Ripps['Value Date'].notna(),'Batch_no']=Ripps[Ripps['Value Date'].notna()]['Reference']
    Ripps.loc[Ripps['Value Date'].isnull(),'Reference_new']=Ripps[Ripps['Value Date'].isnull()]['Reference']
    Ripps['Batch_no'].fillna(method='ffill',inplace=True)
    Ripps['Value Date'].fillna(method='ffill',inplace=True)
    Ripps['Type'].fillna(method='ffill',inplace=True)
    Ripps.insert(4, 'ReferenceB', np.NaN)
    Ripps.insert(3, 'Bname', np.NaN)
    Ripps.insert(2, 'Cname', np.NaN)
    Ripps.insert(1, 'Breference', np.NaN)
    Ripps.insert(0, 'Nreference', np.NaN)
    df1 =  [re.sub(r'[^a-zA-Z]', '', str(x)) for x in Ripps["Ordering Customer/Drawer"]]
    Ripps["Cname"]=df1
    df2 =  [re.sub(r'[^a-zA-Z]', '', str(x)) for x in Ripps["Beneficiary"]]
    Ripps["Bname"]=df2
    Ripps["ReferenceB"]=Ripps["Batch_no"]
    df3=Ripps['Cname'].str[:4]
    df4=Ripps['Amount'].str[:4]
    df5=Ripps['Bname'].str[:4]
    Ripps['Nreference']= df3.astype(str) +""+ df4
    Ripps['Breference']= df5.astype(str) +""+ df4
    Ripps['Nreference']=Ripps['Nreference'].str.replace(",","")
    Ripps['Nreference']=Ripps['Nreference'].str.replace(".","")
    Ripps['Nreference']=Ripps['Nreference'].str.replace(" ","")
    Ripps['Breference']=Ripps['Breference'].str.replace(",","")
    Ripps['Breference']=Ripps['Breference'].str.replace(".","")
    Ripps['Breference']=Ripps['Breference'].str.replace(" ","")
    
    Ripps=Ripps[(Ripps.Status !="transaction is rejected due to error")]
    Ripps['Status'].value_counts()
    print(Ripps.columns)
    return Ripps
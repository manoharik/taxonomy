import os.path

import psycopg2
import pandas as pd




from pathlib import Path
from statistics import NormalDist
from sdv.single_table import TVAESynthesizer

from ctgan import CTGAN
from sdv.evaluation.single_table import evaluate_quality
from sdv.metadata import SingleTableMetadata


# import import_ipynb
# from syntheticDataGen import *
from pandas import DataFrame
import numpy as np
import json

conn = psycopg2.connect(
    database='myTool',
    user='postgres',
    password='123',
    host='localhost',
    port='5432'
)
conn.autocommit = True
cursor = conn.cursor()


def getpopulation(data, n):
    cols = colArray(data)

    ctgan = CTGAN(batch_size=50, epochs=5, verbose=False)
    ctgan.fit(data, cols)
    ctgan.save('ctgan-risk-demand.pkl')
    samples = ctgan.sample(n)
    return samples

def getpopulationTVAE(df_real,n):
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data=df_real)

    tvae = TVAESynthesizer(
        metadata=metadata,  # <-- required now
        epochs=300
    )
    tvae.fit(df_real)
    synthetic_df = tvae.sample(num_rows=1000)


    return synthetic_df



def evaluate_synth_quality( new_data, data):
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data=data)
    quality_report = evaluate_quality( real_data=data, synthetic_data=new_data, metadata=metadata)
    print(quality_report)
    return quality_report

def colArray(data):
    colHeadreal = []
    for col in data.columns:
        colHeadreal.append(col)
    return colHeadreal


def arrayDBtest(colHeadreal):
    Word = str(colHeadreal)
    sql = "INSERT INTO public.riskarrayteste(typer)VALUES ( Array" + format(Word) + ")"
    #print(sql)
    # cursor.execute(sql)


def insertDataset(datasetName, country, domain):
    sql = "INSERT INTO public.dataset_meta( dsetname, country, domain) VALUES ('" + datasetName + "'," + str(
        country) + "," + str(domain) + ")"
    cursor.execute(sql)
    #print("Project data has been entered successfully !!")

def insertOriginaldatasetfile(datasetid, resords ):
    d = resords.to_json(orient='records')
    sql = "INSERT INTO public.originaldatasetfile( datasetid, resords ) VALUES (" + str(datasetid) + " ,'" + d + "')"
    cursor.execute(sql)


def updatedatasetfile(datasetid, resords ):
    d = resords.to_json(orient='records')
    sql = "UPDATE public.datasetfile set resords= '"+ d + "' where  datasetid= "+ str(datasetid)
    cursor.execute(sql)




def getDatabaseId(datasetName):
    if ('(' in datasetName or '[' in datasetName):
        datasetName = eval(datasetName)

    if(datasetName.__class__.__name__ == 'tuple'):
        datasetName = datasetName[0]
    else:
        pass
    sql = "SELECT id FROM public.dataset_meta where dsetname='" + datasetName + "'"
    cursor.execute(sql)
    row = cursor.fetchone()
    return row[0]

def getAuxDatabaseId(datasetName):

    if ('(' in datasetName or '[' in datasetName):
        datasetName = eval(datasetName)

    if (datasetName.__class__.__name__ == 'tuple'):
        datasetName = datasetName[0]
    else:
        pass
    sql = "SELECT id FROM public.aux_dataset_meta where dsetname='" + datasetName + "'"

    cursor.execute(sql)
    row = cursor.fetchone()

    return row[0]
def getAllDatasets():
    sql = "SELECT dsetname FROM public.dataset_meta "
    cursor.execute(sql)
    row = cursor.fetchall()
    return row




def insertRiskyRecords(datasetId, riskType, combinationNo, numRiskyRec, combinationCol, riskyRecs):
    Word = str(combinationCol)
    d = riskyRecs.to_json(orient='records')
    sql = "INSERT INTO public.riskyrecords( datasetid, risktype, combinationno,numRiskyRec, combinationcol, riskyrecs) VALUES (" + str(
        datasetId) + "," + str(riskType) + "," + str(combinationNo) + "," + str(numRiskyRec) + ",ARRAY" + format(
        Word) + ",'" + d + "')"
    cursor.execute(sql)


def insertRiskSummary(datasetId, risktype):

    sql = "INSERT INTO public.risksummary(datasetid, risktype, numrec) SELECT datasetid, risktype, (select sum(numriskyrec) as numrec WHERE datasetid=" + str(
        datasetId) + " and risktype=" + str(
        risktype) + " group by datasetid,risktype ) FROM public.riskyrecords WHERE datasetid=" + str(
        datasetId) + " and risktype=" + str(risktype) + " group by datasetid,risktype "

    cursor.execute(sql)



def updateGapAccAlgo(datasetId):
    sql = " INSERT INTO public.riskyrecords( datasetid, risktype, combinationno, numriskyrec, combinationcol, riskyrecs) select datasetid, risktype, combinationno, numriskyrec, combinationcol, riskyrecs from riskyrecords where datasetid="+str(datasetId)+" and id in (select id from riskyrecords where combinationcol in( 	select combinationcol from riskyrecords where datasetid="+str(datasetId)+" and risktype=8) and combinationcol not in (select combinationcol from riskyrecords where datasetid="+str(datasetId)+" and risktype=2)) "

    cursor.execute(sql)
    sql = "update public.risksummary set numrec=(select sum(numriskyrec) as numrec FROM public.riskyrecords WHERE datasetid=" + str( datasetId) + " and risktype=2 group by datasetid,risktype ) where datasetid = "+str(datasetId)+" and risktype =2 "

    cursor.execute(sql)

    return 0

def insertcopulauniqueness(datasetid, risktype, combinationno, riskyrecs):
    d = riskyrecs.to_json(orient='records')
    sql = "INSERT INTO public.copulauniqueness( datasetid, risktype, combinationno, riskyrecs) VALUES (" + str(
        datasetid) + "," + str(risktype) + "," + str(combinationno) + ",'" + d + "')";

    cursor.execute(sql)


def removeAllSavedCopulaUniqueness(datasetId, riskType):
    sql = "DELETE FROM public.copulauniqueness WHERE datasetid=" + str(datasetId) + " and risktype=" + str(riskType)
    cursor.execute(sql)


def removeAllSavedRiskyRecords(datasetId, riskType):
    sql = "DELETE FROM public.riskyrecords WHERE datasetid=" + str(datasetId) + " and risktype=" + str(riskType)
    cursor.execute(sql)

def removeAllSavedRiskySummary(datasetId, riskType):
    sql = "DELETE FROM public.risksummary WHERE datasetid=" + str(datasetId) + " and risktype=" + str(riskType)
    cursor.execute(sql)
def removeAllSavedRiskySummary(datasetId, risktype):
    sql = "DELETE FROM public.risksummary WHERE datasetid=" + str(datasetId) + " and risktype=" + str(risktype)
    cursor.execute(sql)


def checkRiskCombAlreadyExist(datasetId, riskType, combination):
    Word = str(combination)
    sql = "SELECT id FROM public.riskyrecords WHERE datasetid=" + str(datasetId) + " and risktype=" + str(
        riskType) + " and combinationcol=Array" + format(Word)
    # sql = "SELECT count(*) FROM public.riskyrecords WHERE datasetid="+str(datasetId)+" and risktype="+str(riskType)+" and combinationcol=Array"+format(Word)

    cursor.execute(sql)
    x = 0
    row = cursor.fetchone()
    if row is None:
        x = 0
    else:
        x = row[0]
    return x


'''
def getPopulationUniqueData(datasetId, riskType):
    sql = "SELECT id FROM public.riskyrecords WHERE datasetid=" + str(datasetId) + " and risktype=" + str(
        riskType) + " and combinationcol=Array" + format(Word)
    # sql = "SELECT count(*) FROM public.riskyrecords WHERE datasetid="+str(datasetId)+" and risktype="+str(riskType)+" and combinationcol=Array"+format(Word)

    cursor.execute(sql)
    x = 0
    row = cursor.fetchone()
    if row is None:
        x = 0
    else:
        x = row[0]
    return x
'''
def viewCopulaUniqueRecords(datasetId, risktype):
    sql = "SELECT riskyrecs FROM public.copulauniqueness WHERE datasetid=" + str(datasetId) + " and risktype=" + str(risktype)
    res = cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        x = 0
    else:
        x = row[0]
    return x

    return x

def viewRiskyRecordsDF(datasetId, riskType):
    df = []
    sql = "SELECT riskyrecs FROM public.copulauniqueness WHERE datasetid=" + str(datasetId) + " and risktype=" + str(
        riskType)
    res = cursor.execute(sql)

    # df = DataFrame(res.fetchone())
    # df.columns = res.keys()
    # x=0
    row = cursor.fetchone()
    if row is None:
        df = []
    else:
        x = row[0]
        df = pd.json_normalize(x)

    return df
def viewRecordsDF(datasetId):
    sql = "SELECT resords 	FROM public.datasetfile where datasetid="+ str(datasetId)
    res = cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        df = 0
    else:
        x = row[0]
        df = pd.json_normalize(x)

    return df

# comb =['yb','Income']
# dbInitialSetup()
# removeAllSavedCopulaUniqueness(1,1)
# data = pd.read_csv(r"D:\Reidentification risk\Taxonomy\Datasets\marketing campaign\copula-test-mark-data.csv")
# size =1000
# df = getpopulation(data,size)
# print(df.shape[0])
# df = pd.DataFrame(data)
# datasetName="dddd"
# colHeadreal = colArray(data)
# d = df.to_json(orient='records')
# x = df.shape[0]
# insertDataset(datasetName,1,1)
# insertRiskyRecords(1,2,5,x,colHeadreal,d)
# removeAllSavedRiskySummary(1,2)
# insertRiskSummary(1,2)
# getDatabaseId("Marketting")
# removeAllSavedRiskyRecords(1,2)
# print( checkRiskCombAlreadyExist(1,2,comb))

# sss = viewRiskyRecords(1, 1)
# print(sss)

# print(df2)
def updateRiskyRecords(dbid, tot, newtot , risktype):

    sql = "select numriskyrec from riskyrecords where risktype="+str(risktype)+" and datasetid="+str(dbid)
    numrisky = cursor.execute(sql)
    row = cursor.fetchone()

    y = row[0] * tot/newtot
    y = int(y)
    sql = "UPDATE public.riskyrecords SET numriskyrec ="+str(y)+" WHERE datasetid ="+str(dbid)+" and risktype ="+str(risktype)
    cursor.execute(sql)

def alreadyExistRiskCalculation(dataset_id,risktype_id):
    sql = "select numriskyrec from riskyrecords where risktype=" + str(risktype_id) + " and datasetid=" + str(dataset_id)
    numrisky = cursor.execute(sql)
    row = cursor.fetchone()

    y = row[0]
    if y==0:
        return 0
    else:
        return 1

def insertDatasetMeta(dsetname, country, domain, combinationcol, numrows):
    Word = str(combinationcol)
    sql = "INSERT INTO public.dataset_meta( dsetname, country, domain, combinationcol, numrows) VALUES ('"+ dsetname + "'," + str(country) + "," + str(domain) + ",Array"+format(Word)+","+str(numrows)+")"

    cursor.execute(sql)



def insertDatasetFile(datasetid, numrecords,  combinationcol, resords, filepath,dataframe):
    Word = str(combinationcol)
    d = dataframe.to_json(orient='records')
    sql = "INSERT INTO public.datasetfile(datasetid, numrecords,  combinationcol, resords, filepath) VALUES ("+str(datasetid)+","+str(numrecords)+",Array"+format(Word)+",'"+d+"','"+filepath+"')"

    cursor.execute(sql)


def insertAuxDatasetMeta(dsetname, country, domain, combinationcol, numrows):
    Word = str(combinationcol)
    sql = "INSERT INTO public.aux_dataset_meta( dsetname, country, domain, combinationcol, numrows) VALUES ('"+ dsetname + "'," + str(country) + "," + str(domain) + ",Array"+format(Word)+"," + str(country) + ")"

    cursor.execute(sql)



def insertAuxDatasetFile(datasetid, combinationcol, resords, filepath,dataframe):
    Word = str(combinationcol)
    d = dataframe.to_json(orient='records')
    sql = "INSERT INTO public.auxdatasetfile(datasetid, combinationcol, resords, filepath) VALUES ("+str(datasetid)+",Array"+format(Word)+",'"+d+"','"+filepath+"')"

    cursor.execute(sql)



def insertDatasetThreshold(dataset_meta_id, threshold):
    cursor_ = conn.cursor()
    sql = "SELECT id, datasetid, threshold FROM public.datasetthreshold where datasetid="+str(dataset_meta_id)
    res = cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        sql = f"INSERT INTO public.datasetthreshold( datasetid, threshold) VALUES ('{dataset_meta_id}', {threshold})"
        cursor_.execute(sql)

    else:
        sql = "UPDATE public.datasetthreshold SET threshold="+str(threshold)+" WHERE datasetid="+str(dataset_meta_id)
        cursor_.execute(sql)

    return 0

def getDatasetThreshold(dataset_meta_id):
    sql = "SELECT id, datasetid, threshold FROM public.datasetthreshold where datasetid=" + str(dataset_meta_id)
    res = cursor.execute(sql)
    row = cursor.fetchone()
    x=0
    if row is None:
        x = 1
    else:
        x = row[0]
    return x
    


def checkDataSetMetaExistsByName(dataset_name):
    cursor_ = conn.cursor()
    country_query = f"SELECT Count(*) FROM public.dataset_meta where dsetname='{dataset_name}';"
    cursor_.execute(country_query)
    count = cursor_.fetchone()[0]
    return count > 0

def checkAuxDataSetMetaExistsByName(dataset_name):
    cursor_ = conn.cursor()
    country_query = f"SELECT Count(*) FROM public.aux_dataset_meta where dsetname='{dataset_name}';"
    cursor_.execute(country_query)
    count = cursor_.fetchone()[0]
    return count > 0


def getCountries():
    cursor_ = conn.cursor()
    country_query = 'select * from public.country;'
    cursor_.execute(country_query)
    countries = cursor_.fetchall()
    country_names = [country[1] for country in countries]
    return countries, country_names


def getDomains():
    cursor_ = conn.cursor()
    domain_query = 'select * from public.domain;'
    cursor_.execute(domain_query)
    domains = cursor_.fetchall()
    domain_names = [domain[1] for domain in domains]
    return domains, domain_names


def getAllDatasetMeta():
    cursor_ = conn.cursor()
    sql = "SELECT * FROM public.dataset_meta"
    cursor_.execute(sql)
    dataset_meta = cursor_.fetchall()
    dataset_names = [dm[1] for dm in dataset_meta]
    return dataset_meta, dataset_names


def getriskBreakdown(datasetId):
    sql = "select numrows from dataset_meta where id=" + str(datasetId)
    res = cursor.execute(sql)
    row = cursor.fetchone()
    return row[0]

def checkCalculatedFactors(datasetId):
    sql = "SELECT risktype, count(risktype)FROM public.riskyrecords where datasetid=" + str(datasetId) + " and risktype in (1,2,3)group by datasetid, risktype "
    res = cursor.execute(sql)
    row = cursor.rowcount
    return row

def getTotalrisk(datasetId):
    totalRec = getriskBreakdown(datasetId)

    sql = "SELECT  datasetid, avg(numriskyrec)/" + str(
        totalRec) + " as risk FROM public.riskyrecords where datasetid=" + str(datasetId) + "  group by datasetid "
    res = cursor.execute(sql)
    row = cursor.fetchone()
    return row

def getTotalrisk_asmax(datasetId):
    totalRec = getriskBreakdown(datasetId)

    sql = ("select max(risk) as risk,min(accuracy) as accuracy from risk_cal_summary where dataset_id="+str(datasetId))
    res = cursor.execute(sql)
    row = cursor.fetchone()
    return row

def insertTotalRisk(datasetid, risk):
    sql = "delete from public.totalrisk where datasetid="+str(datasetid)
    cursor.execute(sql)
    sql = "INSERT INTO public.totalrisk(datasetid, totalrisk) VALUES ("+str(datasetid)+", "+str(risk)+")"
    cursor.execute(sql)
    print("Total Risk Saved successfully !!")


def getNumRows(datasetId,totalRec):
    sql = "SELECT  datasetid, avg(numriskyrec)/" + str(
        totalRec) + " as risk FROM public.riskyrecords where datasetid=" + str(datasetId) + "  group by datasetid "
    res = cursor.execute(sql)
    row = cursor.fetchone()
    return row


def getDataframebyID1(datasetId):

    sql = "SELECT filepath,resords FROM public.datasetfile WHERE datasetid=" + str(datasetId)

    res = cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        df = 0
    else:
        x = row[1]
        if x is None:
            str_path = row[0]
            path = Path(str_path)
            data = pd.read_csv(path)
            #data = pd.read_csv(r"D:\Reidentification risk\Taxonomy\Datasets\xyz-wd.csv")
            df = pd.DataFrame(data)
            print(df.shape[0])
        else:
            df = pd.json_normalize(x)

    return df
def getAuxDataframebyID(datasetId):


    sql = "SELECT filepath,resords FROM public.auxdatasetfile WHERE datasetid=" + str(datasetId)

    res = cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        df = 0
    else:
        x = row[1]
        if x is None:
            str_path = row[0]
            print(str_path)
            path = Path(str_path)
            data = pd.read_csv(path)
            #data = pd.read_csv(r"D:\Reidentification risk\Taxonomy\Datasets\xyz-wd.csv")
            df = pd.DataFrame(data)
        else:
            df = pd.json_normalize(x)

    return df

def getRiskyRecordDF(datasetid,risktype):
    df = pd.DataFrame()
    sql = "select riskyrecs from riskyrecords where datasetid="+str(datasetid)+" and risktype="+str(risktype)+" limit 1"
    res = cursor.execute(sql)
    row = cursor.fetchone()
    if row is not None:
        x = row[0]
        df = pd.json_normalize(x)
    return df


def getDataframebyID(datasetId):
    sql = "SELECT filepath,resords FROM public.datasetfile WHERE datasetid=" + str(datasetId)

    res = cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        df = 0
    else:
        x = row[1]
        if x is None:
            str_path = row[0]

            path = Path(str_path)
            data = pd.read_csv(path)
            #data = pd.read_csv(r"E:\Reidentification risk\Taxonomy\Datasets\xyz-wd.csv")
            df = pd.DataFrame(data)
        else:
            df = pd.json_normalize(x)

    return df


def getDatasetMeta(datasetId):
    sql = "SELECT dsetname, country, domain, combinationcol FROM public.dataset_meta where id=" + str(datasetId) + ""
    cursor.execute(sql)
    row = cursor.fetchone()
    return row

def getAuxDatasetMeta(datasetId):
    sql = "SELECT dsetname, country, domain, combinationcol FROM public.aux_dataset_meta where id=" + str(datasetId) + ""
    cursor.execute(sql)
    row = cursor.fetchone()
    return row


def getCountryEqlDset(countryid):
    sql = "SELECT id,dsetname, country, domain,combinationcol FROM public.dataset_meta where country=" + str(
        countryid) + ""
    cursor.execute(sql)
    row = cursor.fetchone()
    return row


def getColumnArray(countryid, datasetId):
    if countryid != 0:
        sql = "SELECT id, combinationcol FROM public.dataset_meta where country=" + str(countryid) + " and id!=" + str(
            datasetId)
    else:
        sql = "SELECT id, combinationcol FROM public.dataset_meta"
    cursor.execute(sql)
    row = cursor.fetchall()
    return row

def getColumnArray(countryid, datasetId):
    if countryid != 0:
        sql = "SELECT id, combinationcol FROM public.dataset_meta where country=" + str(countryid) + " and id!=" + str(
            datasetId)
    else:
        sql = "SELECT id, combinationcol FROM public.dataset_meta"
    cursor.execute(sql)
    row = cursor.fetchall()
    return row

def getAuxColumnArray(countryid, datasetId):
    if countryid != 0:
        sql = "SELECT id, combinationcol FROM public.aux_dataset_meta where country=" + str(countryid)
    else:
        sql = "SELECT id, combinationcol FROM public.aux_dataset_meta"
    #print(sql)
    cursor.execute(sql)
    row = cursor.fetchall()
    return row




def insertdatasetfile(datasetId, dataset, filename, numrecords):
    combinationCol = colArray(dataset)
    Word = str(combinationCol)
    d = dataset.to_json(orient='records')
    sql = "INSERT INTO public.datasetfile( datasetid, numrecords,  combinationcol, resords,filepath) VALUES (" + str(
        datasetId) +","+str(numrecords) + ",ARRAY" + format(Word) + ",'" + d + "','" + filename + "')"
    cursor.execute(sql)


def insertCommonCol(datasetid1, col1, foreigndatasetid1, foreigncol1):
    sql = "INSERT INTO public.commoncol( datasetid, col, foreigndatasetid, foreigncol)	VALUES (" + str(
        datasetid1) + ", '" + col1 + "'," + str(foreigndatasetid1) + ",'" + foreigncol1 + "')"
    print(sql)
    cursor.execute(sql)

def insertAuxCommonCol(datasetid1, col1, foreigndatasetid1, foreigncol1):
    sql = "INSERT INTO public.commonauxcol( datasetid, col, foreigndatasetid, foreigncol)	VALUES (" + str(
        datasetid1) + ", '" + col1 + "'," + str(foreigndatasetid1) + ",'" + foreigncol1 + "')"
    print(sql)
    cursor.execute(sql)

def insertRiskCalSummary(datasetid, risktypeid, risk, accuracy):
    sql = "INSERT INTO public.risk_cal_summary( dataset_id, risk_type_id, risk, accuracy)	VALUES (" + str(
        datasetid) + ", " + str(risktypeid) + "," + str(risk) + "," + str(accuracy) + ")"
    print(sql)
    cursor.execute(sql)

def check_already_RiskCalSummary(datasetid,risktypeid):
    df =0
    sql = "select risk from public.risk_cal_summary where dataset_id="+str(datasetid)+" and risk_type_id="+str(risktypeid)+" limit 1"
    res = cursor.execute(sql)
    row = cursor.fetchone()
    return row

def viewCommonAuxCol(datasetId,fdatasetId):
    sql = "select dataset_id,risktype.description, risk_cal_summary.risk,risk_cal_summary.accuracy from risk_cal_summary, risktype where risk_cal_summary.risk_type_id=risktype.id and risk_cal_summary.dataset_id="+str(datasetId)
    res = cursor.execute(sql)

    row = cursor.fetchall()
    return row


def removeAllCommonCol(datasetId):
    sql = "DELETE FROM public.commoncol WHERE datasetid=" + str(datasetId)
    cursor.execute(sql)

def removeAllAuxCommonCol(datasetId):
    sql = "DELETE FROM public.commonauxcol WHERE datasetid=" + str(datasetId)
    cursor.execute(sql)


def viewCommonCol(datasetId,fdatasetId):
    sql = "select  array_agg(col) as col, datasetid, foreigndatasetid, array_agg(foreigncol) as foreigncol from commoncol where datasetid=" + str(
        datasetId) + " and foreigndatasetid=" + str(fdatasetId) + " group by datasetid, foreigndatasetid"
    res = cursor.execute(sql)

    row = cursor.fetchall()
    return row


def viewCommonAuxCol(datasetId,fdatasetId):
    sql = "select  array_agg(col) as col, datasetid, foreigndatasetid, array_agg(foreigncol) as foreigncol from commonauxcol where datasetid=" + str(datasetId) + " and foreigndatasetid="+str(fdatasetId)+" group by datasetid, foreigndatasetid"
    res = cursor.execute(sql)

    row = cursor.fetchall()
    return row

def viewCommonAuxDset(datasetId):
    sql = "SELECT distinct(public.aux_dataset_meta.dsetname) FROM public.commonauxcol,aux_dataset_meta where public.commonauxcol.foreigndatasetid=public.aux_dataset_meta.id and public.commonauxcol.datasetid="+str(datasetId)

    print(sql)
    #sql = "select  array_agg(col) as col, datasetid, foreigndatasetid, array_agg(foreigncol) as foreigncol from commoncol where datasetid=" + str(
     #   datasetId) + " group by datasetid, foreigndatasetid"
    res = cursor.execute(sql)
    # print("ffff")
    # df = DataFrame(res.fetchone())
    # df.columns = res.keys()
    # x=0
    row = cursor.fetchall()
    if(row.__class__.__name__ == 'list'):
        row = [element[0] for element in row]
    print(row)
    return row

def convertDatasettoArr(dset):
    return 0

def viewCommonMainDset(datasetId):
    sql = "SELECT distinct(public.dataset_meta.dsetname) as dset FROM public.commoncol,dataset_meta where public.commoncol.foreigndatasetid=public.dataset_meta.id and public.commoncol.datasetid="+str(datasetId)
    #sql = "select  array_agg(col) as col, datasetid, foreigndatasetid, array_agg(foreigncol) as foreigncol from commoncol where datasetid=" + str(
     #   datasetId) + " group by datasetid, foreigndatasetid"
    res = cursor.execute(sql)
    # print("ffff")
    # df = DataFrame(res.fetchone())
    # df.columns = res.keys()
    # x=0
    row = cursor.fetchall()
    return row

def getDatafilePath():
    strPath = "'D:\Reidentification risk\Taxonomy\Datasets\'"
    return strPath
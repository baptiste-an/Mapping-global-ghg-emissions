from sankey17 import *
from exiobase_functions import *
import zipfile


# if not os.path.exists("Data/EXIO3"):
#     os.mkdir("Data/EXIO3")
# for year in range(1995, 2020, 1):
#     download("https://zenodo.org/record/5589597/files/IOT_" + str(year) + "_pxp.zip", dest_folder="Data/EXIO3")
#     with zipfile.ZipFile("Data/EXIO3/IOT_" + str(year) + "_pxp.zip", "r") as zip_ref:
#         zip_ref.extractall("Data/EXIO3")
#     os.remove("Data/EXIO3/IOT_" + str(year) + "_pxp.zip")

#     path = "Data/EXIO3/IOT_" + str(year) + "_pxp/"
#     feather.write_feather(pd.read_csv(path + "Z.txt", sep="\t", index_col=[0, 1], header=[0, 1]), path + "Z.feather")
#     feather.write_feather(pd.read_csv(path + "Y.txt", sep="\t", index_col=[0, 1], header=[0, 1]), path + "Y.feather")

#     for file in ["Y.txt", "Z.txt", "A.txt"]:
#         os.remove(path + file)

# if not os.path.exists("Data/Kbar"):
#     os.mkdir("Data/Kbar")
# Z = feather.read_feather("Data/EXIO3/IOT_1995_pxp/Z.feather").fillna(0)
# for year in range(1995, 2020, 1):
#     download(
#         "https://zenodo.org/record/7073276/files/Kbar_exio_v3_8_2_" + str(year) + "_cfc_pxp.mat",
#         dest_folder="Data/Kbar",
#     )
#     mat = scipy.io.loadmat("Data/Kbar/Kbar_exio_v3_8_2_" + str(year) + "_cfc_pxp")
#     feather.write_feather(
#         pd.DataFrame(mat["Kbar"].toarray(), index=Z.index, columns=Z.columns).fillna(0),
#         "Data/Kbar/Kbar" + str(year) + ".feather",
#     )

# Y_all()
# L_and_Lk()
# SLY()

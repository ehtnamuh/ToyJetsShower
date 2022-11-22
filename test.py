import pickle
import json
import numpy as np
input_jet = 'tree_2_truth_0'

input_dir= 'data/truth/'

fd = open(input_dir+ str(input_jet) + '.pkl', "rb")
jet_dic = pickle.load(fd, encoding='latin-1')
# print('jet dictionary List =',jet_dic[1]["leaves"])
fd.close()

jet_json_format = {}
jet_json_format["tree"] = jet_dic[1]["tree"].tolist()
jet_json_format["content"] =  jet_dic[1]["content"].tolist()
jet_json_format["leaves"] = jet_dic[1]["leaves"].tolist()

# save to json format
with open("blender/data/test.json","w") as f:
    json.dump(jet_json_format,f, indent=2)


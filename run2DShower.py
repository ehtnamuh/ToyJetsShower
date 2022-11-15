import numpy as np
import torch
import pprint
import matplotlib.pyplot as plt
import sys
import pickle
import argparse
import logging
import os

from showerSim import exp2DShowerTree
from showerSim.utils import get_logger


logger = get_logger(level=logging.INFO)

augmented_data=False

# Nsamples=sys.argv[1]
# start = int(sys.argv[2])
# end = int(sys.argv[3])
#-----------------------
'''
Gaussian distribution shower
'''
parser = argparse.ArgumentParser(description="Generate synthetic jets")
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Increase output verbosity"
)

parser.add_argument(
    "--Nsamples", type=int, required=True, help="Number of jet samples"
)

parser.add_argument(
    "--jetType", type=str, required=True, help="Input jet type, e.g. 'QCDjets' or 'Wjets' "
)

parser.add_argument(
    "--id", type=str, default=0, help="dataset id"
)


args = parser.parse_args()


# input_scale = torch.tensor(4*[[100.]])
# Delta_0 = torch.tensor([[60.]])
# rate=torch.tensor(10.)

rate2=torch.tensor(8.)
#
# rate=torch.tensor(3.6)



# rate=torch.tensor(3.6)
# jetPT = torch.tensor([10000.,10000.])
jetPT = torch.tensor([0.,0.])




## Values that result in a poor performance for beam search

rate=torch.tensor(2.)
Delta_start = 0.4
pt_min = 0.008

# rate=torch.tensor(2.2)
# Delta_start = 0.4
# pt_min = 0.006
 ##########

# rate=torch.tensor(10.)
# Delta_start = 0.2
# # pt_min = 0.004
# pt_min = 0.08

# Delta_start = 200
# pt_min = 0.4

# for i in range(start,end):

# Values that give ~ 50 leaves, typically with px,py >0 for all of them.
# simulator = exp2DShowerTree.Simulator(jet_p=[800.,600.], rate=4, Mw=80., pt_cut=0.04)


if args.jetType == "Wjets":
    simulator = exp2DShowerTree.Simulator(jet_p=torch.tensor([500.,400.]), Mw=torch.tensor(80.), pt_cut=0.04, Delta_0=60., num_samples=int(args.Nsamples))

elif args.jetType == "QCDjets":
    simulator = exp2DShowerTree.Simulator(jet_p=torch.tensor([500.,400.]), Mw=None, pt_cut=0.04, Delta_0=60., num_samples=int(args.Nsamples))

elif args.jetType == "Topjets":
    simulator = exp2DShowerTree.Simulator(jet_p=torch.tensor([500.,400.]), Mw=torch.tensor(173.), pt_cut=0.04, Delta_0=60., num_samples=int(args.Nsamples))

elif args.jetType == "TrellisMw300":
    ## TRELLIS
    jetPT = torch.tensor([0., 0.])
    rate = torch.tensor(10.)
    Delta_start = 0.2
    # pt_min = 0.004
    pt_min = 0.08
    simulator = exp2DShowerTree.Simulator(jet_p=jetPT, Mw=torch.tensor(300.), pt_cut=pt_min, Delta_0=60., num_samples=int(args.Nsamples))

elif args.jetType == "TrellisMw01":
    ## TRELLIS
    jetPT = torch.tensor([0., 0.])
    rate = torch.tensor(2.2)
    Delta_start = 0.4
    pt_min = 0.006
    simulator = exp2DShowerTree.Simulator(jet_p=jetPT, Mw=torch.tensor(0.1), pt_cut=pt_min, Delta_0=60., num_samples=int(args.Nsamples))

elif args.jetType == "TrellisMw01B":
    ## TRELLIS
    jetPT = torch.tensor([0., 0.])
    rate = torch.tensor(2.)
    Delta_start = 0.4
    pt_min = 0.008
    simulator = exp2DShowerTree.Simulator(jet_p=jetPT, Mw=torch.tensor(0.1), pt_cut=pt_min, Delta_0=60., num_samples=int(args.Nsamples))


else:
    print(args.jetType)
    raise ValueError(f"Please choose a valid jet type (QCDjets, Wjets or Topjets)")

# Values for tests
# simulator = exp2DShowerTree.Simulator(jet_p=jetPT, pt_cut=pt_min, Delta_0=Delta_start, num_samples=int(args.Nsamples))
simulator = exp2DShowerTree.Simulator(jet_p=jetPT,Mw=torch.tensor(0.1), pt_cut=pt_min, Delta_0=Delta_start, num_samples=int(args.Nsamples))

# simulator = exp2DShowerTree.Simulator(jet_p=torch.tensor([400.,250.]), Mw=torch.tensor(80.), pt_cut=1, Delta_0=60., num_samples=1)
# simulator = exp2DShowerTree.Simulator(jet_p=[800.,600.], rate=10, pt_cut=0.5)
#simulator = Simulator(sensitivities=True)





if not augmented_data:
  jet_list = simulator(rate)

  logger.debug(f"---"*10)
  logger.debug(f"jet_list = {jet_list}")

else:

  jet_list, joint_score, joint_log_ratio, joint_log_prob = simulator.augmented_data(rate,
                                                                                    None,
                                                                                    rate2,
                                                                                    exponential=True,
                                                                                    uniform=False)



  logger.info(f"---"*10)
  logger.debug(f"jet_list = {jet_list}")
  logger.info(f"joint_score = {joint_score}")
  logger.info(f"joint_log_likelihood_ratio= {joint_log_ratio}")
  logger.info(f"joint_log_prob= {joint_log_prob}")
  logger.info(f"---"*10)




  def jet_log_likelihood():

    Lambda = jet_list[0]['Lambda']
    log_likelihood = 0

    if Lambda.requires_grad:
      Lambda=Lambda.detach().numpy()

    for entry in jet_list[0]['draws'][1::]:
      #     if entry!=-1:
      if entry.requires_grad:
        entry = entry.detach().numpy()

      log_likelihood += np.log(Lambda * np.exp(-Lambda * entry))

    return log_likelihood


  jet_log_likelihood_cross_check=jet_log_likelihood()
  logger.info(f" jet_log_likelihood cross-check = {jet_log_likelihood_cross_check}")
  #---------------------------



ToyModelDir = "/home/samin/Desktop/Projects/CERN/Ginko/ToyJetsShower/scratch/sm4511/ToyJetsShower/data/"+args.jetType
TreeAlgoDir = "/home/samin/Desktop/Projects/CERN/Ginko/ToyJetsShower/scratch/sm4511/TreeAlgorithms/data/"+args.jetType+"/Truth/"

os.system("mkdir -p "+ToyModelDir)
os.system("mkdir -p "+TreeAlgoDir)

simulator.save(jet_list, TreeAlgoDir, "tree_" + str(args.Nsamples) + "_truth_" + str(args.id))
simulator.save(jet_list, ToyModelDir, "tree_"+str(args.Nsamples)+"_truth_"+str(args.id))



# simulator.save(jet_list, "../TreeAlgorithms/data/truth", "tree_" + str(Nsamples) + "_truth_" + str(i))
# simulator.save(jet_list, "./data/truth", "tree_"+str(Nsamples)+"_truth_"+str(i))


# To run: python run2DShower.py --Nsamples=2 --id=0
from controller_utils.ui_struct.UI_SimulationInfo import UI_SimulationInfo
from controller_utils.ui_struct.UI_Participant import UI_Participant
from controller_utils.ui_struct.UI_Coupling import UI_Coupling
from controller_utils.myutils.UT_PCErrorLogging import UT_PCErrorLogging
from controller_utils.ui_struct.UI_Coupling import UI_CouplingType


class UI_UserInput(object):
    """
    This class represents the main object that contains either one YAML file
    or a user input through a GUI

    The main components are:
     - the list of participants
     - general simulation informations
    """
    def __init__(self):
        """The constructor, dummy initialization of the fields"""
        self.sim_info = UI_SimulationInfo()
        self.participants = {} # empty participants stored as a dictionary
        self.couplings = []    # empty coupling list
        pass

    def init_from_yaml(self, etree, mylog: UT_PCErrorLogging):
        # Check if using new topology structure
        if "coupling-scheme" in etree and "participants" in etree and "exchanges" in etree:
            # --- Parse simulation info from 'coupling-scheme' ---
            simulation_info = etree["coupling-scheme"]
            self.sim_info.sync_mode = simulation_info.get("sync-mode", "on")
            self.sim_info.mode = simulation_info.get("mode", "fundamental")
            self.sim_info.steady = False
            self.sim_info.NrTimeStep = simulation_info.get("max-time", 1e-3)
            self.sim_info.Dt = simulation_info.get("time-window-size", 1e-3)
            self.sim_info.accuracy = "medium"

            # --- Parse participants ---
            self.participants = {}
            participants_data = etree["participants"]
            for participant_name, solver_info in participants_data.items():
                new_participant = UI_Participant()
                new_participant.name = participant_name
                new_participant.solverName = solver_info
                new_participant.solverType = ""  # Placeholder; adjust if solver-type info available
                new_participant.list_of_couplings = []
                self.participants[participant_name] = new_participant

            # --- Parse couplings from exchanges ---
            exchanges_list = etree["exchanges"]
            # Group exchanges by unique participant pairs
            groups = {}
            for exchange in exchanges_list:
                pair = tuple(sorted([exchange["from"], exchange["to"]]))
                groups.setdefault(pair, []).append(exchange)

            self.couplings = []
            for pair, ex_list in groups.items():
                coupling = UI_Coupling()
                p1_name, p2_name = pair
                coupling.partitcipant1 = self.participants[p1_name]
                coupling.partitcipant2 = self.participants[p2_name]

                # Determine coupling type based on exchanged data
                data_names = {ex["data"] for ex in ex_list}
                if "Force" in data_names and "Displacement" in data_names:
                    coupling.coupling_type = UI_CouplingType.fsi
                elif "Force" in data_names:
                    coupling.coupling_type = UI_CouplingType.f2s
                elif "Temperature" in data_names:
                    coupling.coupling_type = UI_CouplingType.cht
                else:
                    coupling.coupling_type = UI_CouplingType.error_coupling

                # Use the first exchange's patches as boundary interfaces (simple heuristic)
                first_ex = ex_list[0]
                coupling.boundaryC1 = first_ex.get("from-patch", "")
                coupling.boundaryC2 = first_ex.get("to-patch", "")

                self.couplings.append(coupling)
                coupling.partitcipant1.list_of_couplings.append(coupling)
                coupling.partitcipant2.list_of_couplings.append(coupling)

        else:
            # --- Fallback to original parsing logic for old YAML structures ---
            try:
                simulation_info = etree["simulation"]
                sync_mode = simulation_info.get("sync-mode", "on")
                mode = simulation_info.get("mode", "fundamental")
                self.sim_info.sync_mode = sync_mode
                self.sim_info.mode = mode
                self.sim_info.init_from_yaml(simulation_info, mylog)

                # Parse participants from the old structure
                participants_list = etree["participants"]
                for participant_name in participants_list:
                    participant_data = participants_list[participant_name]
                    new_participant = UI_Participant()
                    new_participant.init_from_yaml(participant_data, participant_name, mylog)
                    self.participants[participant_name] = new_participant

                # Parse couplings from the old structure
                couplings_list = etree["couplings"]
                self.couplings = []
                for couplings in couplings_list:
                    for coupling_name in couplings:
                        coupling_data = couplings[coupling_name]
                        new_coupling = UI_Coupling()
                        new_coupling.init_from_yaml(coupling_name, coupling_data, self.participants, mylog)
                        self.couplings.append(new_coupling)
            except Exception as e:
                mylog.rep_error("Error during YAML initialization: " + str(e))

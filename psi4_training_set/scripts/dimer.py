class Dimer:
    """ Extension class that deals with dimers """

    def __init__(self, molecules):
        self.mols = molecules

    def size(self):
        """ Gives the total atom amount of the dimer """
        total = 0
        for mol in self.mols:
            total += mol.size()
        return total

    def set_energy(self, energy):
        self.energy = energy

    def __repr__(self):
        ret_str = ""
        for mol in self.mols:
            ret_str += str(mol)
        return ret_str

    def energy_str(self):
        """ String representation of energies used in output """
        ret_str = "%.8f"%self.energy
        for mol in self.mols:
            ret_str += " " + mol.energy_str()
        return ret_str

    def int_energy(self):
        """ Interaction energy fo a dimer.
            This is defined by E(AB) - E(A) - E(B), 
            A and B representing molecules
        """
        ret_energy = self.energy
        for mol in self.mols:
            ret_energy -= mol.energy
        return ret_energy
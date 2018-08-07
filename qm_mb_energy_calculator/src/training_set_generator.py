import sys, os, math
# this is messy, I hope there is a better way to do this!
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
import sqlite3
import constants
from database import Database

def generate_1b_training_set(settings, database_name, output_path, molecule_name, method, basis, cp, tag):
    """
    Creates a training set file from the calculated energies in a database.

    Args:
        settings    - .ini file with all relevent settings information
        database_name - filepath to database file
        output_path - path to file to write training set to
        molecule_name - the name of the molecule to generate a training set for
        method      - use energies calculated with this method. Use % for any method
        basis       - use energies calculated with this basis. Use % for any basis
        cp          - use energies calculated with this cp. Use 0 for False, 1 for True, or % for any cp
        tag         - use energies marked with this tag. Use % for any tag

    Return:
        None
    """
    
    # add .db to database name if it doesn't already end in .db 
    if database_name[-3:] != ".db":
        print("Database name \"{}\" does not end in database suffix \".db\". Automatically adding \".db\" to end of database name.".format(database_name))
        database_name += ".db"
    
    # open the database
    database = Database(database_name)

    print("Creating a fitting input file from database {} into file {}".format(database_name, output_path))

    # get list of all [molecule, energies] pairs calculated in the database
    molecule_energy_pairs = list(database.get_energies(molecule_name, method, basis, cp, tag))

    # if there are no calculated energies, error and exit
    if len(molecule_energy_pairs) == 0:
        print("No completed energy entries to generate a training set.")
        database.close()
        exit(1)
    
    # find the optimized geometry energy from the database
    try:
        opt_energies = list(database.get_optimized_energies(molecule_name, method, basis, cp, tag))[0][1]
    except IndexError:
        raise ValueError("No optimized geometry in database. Terminating training set generation.") from None

    # open output file for writing
    output = open(output_path, "w")

    # loop thru each molecule, energy pair
    for molecule_energy_pair in molecule_energy_pairs:
        molecule = molecule_energy_pair[0]
        energies = molecule_energy_pair[1]

        # write the number of atoms to the output file
        output.write(str(molecule.get_num_atoms()) + "\n")

        # monomer interaction energy
        output.write(str((float(energies[0]) - float(opt_energies[0])) * constants.au_to_kcal) + " ") # covert Hartrees to kcal/mol
	
        output.write("\n")

        # write the molecule's atoms' coordinates to the xyz file
        output.write(molecule.to_xyz() + "\n")

    database.close()


def generate_2b_training_set(settings, database_name, output_path, molecule_name, monomer_1_name, monomer_2_name, method, basis, cp, tag):
    """"
    Creates a training set file from the calculated energies in a database.

    Args:
        settings    - .ini file with all relevent settings information
        database_name - filepath to database file
        output_path - path to file to write training set to
        molecule_name - the name of the molecule to generate a training set for
        monomer_1_name - the name of the first monomer in the dimer NOTHING WORKS!
        monomer_2_name - the name of the second monomer in the dimer
        method      - use energies calculated with this method. Use % for any method
        basis       - use energies calculated with this basis. Use % for any basis
        cp          - use energies calculated with this cp. Use 0 for False, 1 for True, or % for any cp
        tag         - use energies marked with this tag. Use % for any tag

    Return:
        None
    """
    
    # add .db to database name if it doesn't already end in .db 
    if database_name[-3:] != ".db":
        print("Database name \"{}\" does not end in database suffix \".db\". Automatically adding \".db\" to end of database name.".format(database_name))
        database_name += ".db"
    
    # open the database
    database = Database(database_name)

    print("Creating a fitting input file from database {} into file {}".format(database_name, output_path))

    # get list of all [molecule, energies] pairs calculated in the database
    molecule_energy_pairs = list(database.get_energies(molecule_name, method, basis, cp, tag))

    # if there are no calculated energies, error and exit
    if len(molecule_energy_pairs) == 0:
        print("No completed energy entries to generate a training set.")
        database.close()
        exit(1)
    
    # find the optimized geometry energy of the two monomers from the database
    try:
        monomer_1_opt_energies = list(database.get_optimized_energies(monomer_1_name, method, basis, cp, tag))[0][1]
        monomer_2_opt_energies = list(database.get_optimized_energies(monomer_2_name, method, basis, cp, tag))[0][1]
    except IndexError:
        raise ValueError("No optimized geometry in database. Terminating training set generation") from None

    # open output file for writing
    output = open(output_path, "w")

    for molecule_energy_pair in molecule_energy_pairs:
        molecule = molecule_energy_pair[0]
        energies = molecule_energy_pair[1]

        # write the number of atoms to the output file
        output.write(str(molecule.get_num_atoms()) + "\n")

        interaction_energy = (energies[2] - energies[1] - energies[1]) * constants.au_to_kcal # covert Hartrees to kcal/mol
        monomer1_energy_formation = (energies[0] - monomer_1_opt_energies[0]) * constants.au_to_kcal # covert Hartrees to kcal/mol
        monomer2_energy_formation = (energies[1] - monomer_2_opt_energies[0]) * constants.au_to_kcal # covert Hartrees to kcal/mol

        binding_energy = interaction_energy - monomer1_energy_formation - monomer2_energy_formation

        # monomer interaction energy
        output.write("{} {} {} {}".format(binding_energy, interaction_energy, monomer1_energy_formation, monomer2_energy_formation))
	
        output.write("\n")

        # write the molecule's atoms' coordinates to the xyz file
        output.write(molecule.to_xyz() + "\n")

    database.close()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Incorrect number of arguments");
        print("Usage: python database_reader.py <settings_file> <database_name> <output_path> <molecule_name>")
        sys.exit(1)   
    generate_1b_training_set(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], "%", "%", "%", "%")

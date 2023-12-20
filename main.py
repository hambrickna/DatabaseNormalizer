import pandas as pd
from form_finder import (
    check_1NF,
    check_2NF,
    check_3NF,
    check_4NF,
    check_5NF,
    check_BCNF,
)
from normalizer import (
    transform_to_1NF,
    transform_to_2NF,
    transform_to_3NF,
    transform_to_BCNF,
    transform_to_4NF,
    transform_to_5NF,
    update_relationNames,
    Relation,
    MultiValuedDependency,
    FunctionalDependency,
)


def get_inputs():

    # First ask user for table as csv file
    input_table = input("Input dataset: ")
    while input_table[-4:] != ".csv":
        print("Invalid input. Please try again.")
        input_table = input("Input dataset: ")

    input_table = "exampleInputTable.csv"

    # Then ask user for functional dependencies as text file
    input_FD = input("Input functional dependencies file: ")
    while input_FD[-4:] != ".txt":
        print("Invalid input. Please try again.")
        input_FD = input("Input functional dependencies file: ")

    input_FD = "exampleFunctionalDependencies.txt"

    # Then ask user for multivalued dependencies as text file
    input_MVD = input("Input multivalued dependencies file: ")
    while input_MVD[-4:] != ".txt":
        print("Invalid input. Please try again.")
        input_MVD = input("Input multivalued dependencies file: ")

    input_MVD = "exampleMultivaluedDependencies.txt"

    df = table_parser(input_table)

    df.name = input_table[:-4]

    # Ask the user for the highest normal form to reach
    Normal_Form = input(
        "Choice of the highest normal form to reach (1: 1NF, 2: 2NF, 3: 3NF, B: BCNF, 4: 4NF, 5: 5NF): "
    )
    while Normal_Form not in ["1", "2", "3", "B", "4", "5"]:
        print("Invalid input. Please try again.")
        Normal_Form = input(
            "Choice of the highest normal form to reach (1: 1NF, 2: 2NF, 3: 3NF, B: BCNF, 4: 4NF, 5: 5NF): "
        )

    # Ask the user if they want us to find the highest normal form of the input table
    highest_Form = input(
        "Find the highest normal form of the input table? (1: Yes, 2: No): "
    )
    while highest_Form not in ["1", "2"]:
        print("Invalid input. Please try again.")
        highest_Form = input(
            "Find the highest normal form of the input table? (1: Yes, 2: No): "
        )

    highest_Form = highest_Form == "1"

    # Ask the user for the primary key of the table
    done = False
    while not done:
        done = True
        key = input("Key (can be composite): ")
        key = key.split(", ")
        for k in key:
            if k not in df.columns:
                print("Invalid input. Please try again.")
                done = False
                break

    # Ask the user to specify any multivalued attributes in the table
    done = False
    while not done:
        done = True
        mvAttribute = input("Multivalued attributes: ")
        mvAttribute = mvAttribute.split(", ")
        if len(mvAttribute) == 1 and mvAttribute[0] == "":
            mvAttribute = None
        else:
            for attribute in mvAttribute:
                if attribute not in df.columns:
                    print("Invalid input. Please try again.")
                    done = False
                    break

    return df, input_FD, input_MVD, Normal_Form, highest_Form, key, mvAttribute


# Parse an input csv file representing a dataset information into a Pandas dataframe structure
def table_parser(input_file: str) -> pd.DataFrame:
    df = pd.read_csv(
        input_file, header=0, sep=",", quotechar='"', encoding="utf8", engine="python"
    )
    print(df)
    return df


# Parse Functional Dependencies from input text file into a list of strings
def FD_parser(input_file: str) -> list:
    FD_list = []
    with open(input_file, "r") as f:
        for line in f:
            if line == "exit":
                break
            FD_list.append(line.strip())
    return FD_list


# Parse multivalued dependencies from input text file into a list of strings
def MVD_parser(input_file: str) -> list:
    MVD_list = []
    with open(input_file, "r") as f:
        for line in f:
            if line == "exit":
                break
            MVD_list.append(line.strip())
    return MVD_list


# Function to find the highest normal form of the input table
def highest_normal_form(relation: Relation, MVDs: list) -> str:
    if check_5NF(relation.table, relation.FDs, MVDs, relation.key):
        return "5NF"
    elif check_4NF(relation.table, relation.FDs, MVDs, relation.key):
        return "4NF"
    elif check_BCNF(relation.table, relation.FDs, relation.key):
        return "BCNF"
    elif check_3NF(relation.table, relation.FDs, relation.key):
        return "3NF"
    elif check_2NF(relation.table, relation.FDs, relation.key):
        return "2NF"
    elif check_1NF(relation.table, relation.key, relation.mvAttributes):
        return "1NF"
    else:
        return "Input table is not in any normal form"


# Main function for testing
def main():
    # Get user input
    (
        df,
        input_FD,
        input_MVD,
        Normal_Form,
        highest_Form,
        pkey,
        mvAttributes,
    ) = get_inputs()

    # Parse the functional and multivalued dependencies from the input file
    FDs = FD_parser(input_FD)
    MVDs = MVD_parser(input_MVD)

    # Print relevant information of the table
    print("\nFunctional Dependencies:")
    print("------------------------")
    for FD in FDs:
        print(FD)
    print()
    print("MultiValued Dependencies:")
    for MVD in MVDs:
        print(MVD)
    print()
    print("Normal Form:", Normal_Form)
    print("Key:", pkey)
    print("Multivalued Attributes:", mvAttributes)

    FDs = [FunctionalDependency(FD) for FD in FDs]
    MVDs = [MultiValuedDependency(MVD) for MVD in MVDs]
    # Relation class structure for each table
    relation = Relation(df, pkey, FDs, MVDs.copy(), "Students", mvAttributes)

    # Highest normal form of input table
    hnf = highest_normal_form(relation, MVDs)

    # List of all relations
    Relations = [relation]

    # Transform the relation to the highest normal form specified by the user
    if Normal_Form == "1":
        Relations = transform_to_1NF(Relations)

    elif Normal_Form == "2":
        Relations = transform_to_2NF(transform_to_1NF(Relations))

    elif Normal_Form == "3":

        Relations = transform_to_3NF(transform_to_2NF(transform_to_1NF(Relations)))

    elif Normal_Form == "B":
        Relations = transform_to_BCNF(
            transform_to_3NF(transform_to_2NF(transform_to_1NF(Relations)))
        )

    elif Normal_Form == "4":
        Relations = transform_to_4NF(
            transform_to_BCNF(
                transform_to_3NF(transform_to_2NF(transform_to_1NF(Relations)))
            ),
            MVDs,
        )

    else:
        Relations = transform_to_5NF(
            transform_to_4NF(
                transform_to_BCNF(
                    transform_to_3NF(transform_to_2NF(transform_to_1NF(Relations)))
                ),
                MVDs,
            )
        )

    # Update relation names
    print("\n------------------------------------")
    print("Updating relation names...\n")
    update_relationNames(Relations)

    if Normal_Form == "B":
        Normal_Form = "BC"

    # Write the output to a text file
    with open("output.txt", "w") as f:
        f.write("Normalized Relations in form (" + Normal_Form + "NF):\n\n")
        for relation in Relations:
            f.write(relation.name + "\n")
            f.write(str(relation.table) + "\n")
            f.write("Key: " + str(relation.key) + "\n")
            f.write("Functional Dependencies:\n")
            for fd in relation.FDs:
                f.write(fd.fd + "\n")
            f.write("\n")

        if highest_Form:
            f.write("Highest Normal Form of input table: " + hnf + "\n")


if __name__ == "__main__":
    main()

from form_finder import (
    check_1NF,
    check_2NF,
    check_3NF,
    check_BCNF,
    check_4NF,
    check_5NF,
    is_superkey,
)
import pandas as pd


class FunctionalDependency:
    def __init__(self, fd: str):
        self.determinant, self.dependent = fd.split(" -> ")
        self.determinants = self.determinant.split(", ")
        self.dependents = self.dependent.split(", ")
        self.fd = fd

    def __iter__(self):
        return iter(
            [self.determinant, self.dependent, self.determinants, self.dependents]
        )

    def __next__(self):
        return [self.determinant, self.dependent, self.determinants, self.dependents]

    def print(self):
        print(self.fd)


class MultiValuedDependency:
    def __init__(self, mvd: str):
        self.determinant, self.dependent = mvd.split(" ->> ")
        self.determinants = self.determinant.split(", ")
        self.dependents = self.dependent.split(", ")
        self.mvd = mvd

    def __iter__(self):
        return iter(
            [
                self.determinant,
                self.dependent,
                self.determinants,
                self.dependents,
                self.mvd,
            ]
        )

    def __next__(self):
        return [
            self.determinant,
            self.dependent,
            self.determinants,
            self.dependents,
            self.mvd,
        ]

    def print(self):
        print(self.mvd)

    def copy(self):
        return MultiValuedDependency(self.mvd)


class Relation:
    def __init__(
        self,
        table: pd.DataFrame,
        key: list[str],
        FDs: list[FunctionalDependency],
        MVDs: list[MultiValuedDependency],
        name: str,
        mvAttributes: list[str],
    ):
        self.table = table  # The table as a pandas dataframe
        self.key = key  # The primary key of the table
        self.FDs = FDs  # The functional dependencies of the relation
        self.MVDs = MVDs  # The multivalued dependencies of the relation
        self.name = name  # The name of the relation
        self.mvAttributes = mvAttributes

    def __iter__(self):
        return iter([self.table, self.key, self.FDs, self.name])

    def __next__(self):
        return [self.table, self.key, self.FDs, self.name]

    def find_FD_Dependent(self, attribute: str) -> list[FunctionalDependency]:
        FDs = []
        for fd in self.FDs:
            if attribute in fd.dependents:
                FDs.append(fd)
        return FDs

    def find_FD_Determinant(self, attribute: str) -> list[FunctionalDependency]:
        FDs = []
        for fd in self.FDs:
            if attribute in fd.determinants:
                FDs.append(fd)
        return FDs

    def find_FD_Determinant(self, attributes: list[str]) -> list[FunctionalDependency]:
        FDs = []
        for fd in self.FDs:
            if all(attribute in fd.determinants for attribute in attributes):
                FDs.append(fd)
        return FDs

    def find_FD_Dependent(self, attributes: list[str]) -> list[FunctionalDependency]:
        FDs = []
        for fd in self.FDs:
            if all(attribute in fd.dependents for attribute in attributes):
                FDs.append(fd)
        return FDs

    def find_MVD_Dependent(self, attribute: str) -> list[MultiValuedDependency]:
        MVDs = []
        for mvd in self.MVDs:
            if attribute in mvd.dependents:
                MVDs.append(mvd)
        return MVDs

    def find_MVD_Determinant(self, attribute: str) -> list[MultiValuedDependency]:
        MVDs = []
        for mvd in self.MVDs:
            if attribute in mvd.determinants:
                MVDs.append(mvd)
        return MVDs

    def find_relationship(self, att1: str, att2: str) -> bool:
        if att1 == att2:
            return True

        # Check if att1 is a dependent of att2
        fds = self.find_FD_Determinant(att2)
        for fd in fds:
            if att1 in fd.dependents:
                return True

        # Check if att1 is a determinant of att2
        fds = self.find_FD_Dependent(att2)
        for fd in fds:
            if att1 in fd.determinants:
                return True

        # No functional dependency found connecting att1 and att2
        return False

    def find_relationship(self, att1: list[str], att2: list[str]) -> bool:
        if att1 == att2:
            return True

        # Check if att1 is a dependent of att2
        fds = self.find_FD_Determinant(att2)
        for fd in fds:
            if all(attribute in fd.dependents for attribute in att1):
                return True

        # Check if att1 is a determinant of att2
        fds = self.find_FD_Dependent(att2)
        for fd in fds:
            if all(attribute in fd.determinants for attribute in att1):
                return True


# Find the minimum size of determinants of a FD in a list of FDs
def min_FD(FDs: list[FunctionalDependency]) -> FunctionalDependency:
    min_fd = FDs[0]
    for fd in FDs:
        if len(fd.determinants) < len(min_fd.determinants):
            min_fd = fd
    return min_fd


def find_name(relations: list[Relation], name: str) -> list[Relation]:
    matching_relations = []
    for relation in relations:
        if relation.name == name:
            matching_relations.append(relation)

    return matching_relations


# Transform the table to 1NF
def transform_to_1NF(relations: list[Relation]) -> list[Relation]:
    new_relations = []
    for relation in relations:

        # Check if the relation is in 1NF
        if check_1NF(relation.table, relation.key, relation.mvAttributes):
            new_relations.append(relation)
            continue

        if relation.mvAttributes is not None:
            for attribute in relation.mvAttributes:
                # Check what FDs the attribute is a determinant and dependent of
                attribute_fds_det = relation.find_FD_Determinant(attribute)
                attribute_fds_dep = relation.find_FD_Dependent(attribute)

                new_relation = Relation(pd.DataFrame(), [], [], [], "", [])

                if attribute in relation.key:
                    # Let the attribute explode as is
                    continue

                # If the attribute is a determinant of at least 1 FD
                if len(attribute_fds_det) > 0:
                    for fd in attribute_fds_det:

                        new_relation = Relation(pd.DataFrame(), [], [], [], "", [])

                        prime_dependent = False
                        # Check if dependent is part of the key
                        for dep in fd.dependents:
                            if dep in relation.key:
                                prime_dependent = True

                        if prime_dependent:
                            continue  # Explode the relation as is
                        else:
                            # Create a new relation with the determinant as the key and then explode the multivalue attribute
                            for det in fd.determinants:
                                new_relation.table[det] = relation.table[det]

                            for dep in fd.dependents:
                                new_relation.table[dep] = relation.table[dep]
                                relation.table.drop(dep, axis=1, inplace=True)

                            new_relation.key = fd.determinants
                            new_relation.name = relation.name + "_" + attribute
                            new_relation.FDs = [fd]
                            relation.FDs.remove(fd)
                            new_relations.append(new_relation)

                    new_relations.append(relation)

                # If the attribute is a dependent a FD
                if len(attribute_fds_dep) > 0:
                    for det in attribute_fds_dep[0].determinants:
                        new_relation.table[det] = relation.table[det]

                    for dep in attribute_fds_dep[0].dependents:
                        new_relation.table[dep] = relation.table[dep]
                        relation.table.drop(dep, axis=1, inplace=True)

                    new_relation.key = attribute_fds_dep[0].determinants
                    new_relation.name = relation.name + "_" + attribute
                    new_relation.FDs = [attribute_fds_dep[0]]
                    relation.FDs.remove(attribute_fds_dep[0])
                    new_relations.append(new_relation)

                    new_relations.append(relation)

                # If the attribute is a determinant of at least 1 FD and a dependent of a FD
                if len(attribute_fds_det) > 0 and len(attribute_fds_dep) > 0:
                    for fd in attribute_fds_det:
                        new_relation = Relation(pd.DataFrame(), [], [], [], "", [])

                        prime_dependent = False
                        # Check if dependent is part of the key
                        for dep in fd.dependents:
                            if dep in relation.key:
                                prime_dependent = True

                        if prime_dependent:
                            continue  # Explode the relation as is
                        else:
                            # Create a new relation with the determinant as the key and then explode the multivalue attribute
                            for det in fd.determinants:
                                new_relation.table[det] = relation.table[det]

                            for dep in fd.dependents:
                                new_relation.table[dep] = relation.table[dep]
                                relation.table.drop(dep, axis=1, inplace=True)

                            new_relation.key = fd.determinants
                            new_relation.name = relation.name + "_" + attribute
                            new_relation.FDs = [fd]
                            relation.FDs.remove(fd)
                            new_relations.append(new_relation)

                    new_relations.append(relation)

                    for det in attribute_fds_dep[0].determinants:
                        new_relation.table[det] = relation.table[det]

                    for dep in attribute_fds_dep[0].dependents:
                        new_relation.table[dep] = relation.table[dep]
                        relation.table.drop(dep, axis=1, inplace=True)

                    new_relation.key = attribute_fds_dep[0].determinants
                    new_relation.name = relation.name + "_" + attribute
                    new_relation.FDs = [attribute_fds_dep[0]]
                    relation.FDs.remove(attribute_fds_dep[0])
                    new_relations.append(new_relation)

                    new_relations.append(relation)

    for relation in new_relations:
        attributes = set(relation.table.columns)

        for attribute in attributes:
            if relation.table[attribute].dtype == "object":
                relation.table = relation.table.explode(attribute)

        relation.mvAttributes = None

    for relation in new_relations:
        if not check_1NF(relation.table, relation.key, relation.mvAttributes):

            new_relations.remove(relation)
            r = transform_to_1NF([relation])
            for i in r:
                new_relations.append(i)

    return new_relations


def transform_to_2NF(relations: list[Relation]) -> list[Relation]:
    new_relations = []
    for relation in relations:

        # Check if the relation is in 2NF
        if check_2NF(relation.table, relation.FDs, relation.key):
            new_relations.append(relation)
            continue

        partial_dependencies = []
        # Check each FD to see if it is a partial dependency
        for fd in relation.FDs:
            partial = False
            if fd.determinant != relation.key:
                for det in fd.determinants:
                    # If the determinant is a subset of the key then it is a partial dependency of the key
                    if det in relation.key:
                        partial_dependencies.append(fd)
                        break

                    # If the determinant is not a subset of the key, but a determinant of more then 1 FD then there is a partial dependency somewhere
                    if len(relation.find_FD_Determinant(det)) > 1:
                        # The smaller of the FDs is guaranteed to be a partial dependency
                        # If there is more then 2 partial dependencies it will catch it in the next iteration
                        partial_dependencies.append(
                            min_FD(relation.find_FD_Determinant(det))
                        )
                        break

        # Decompose partial dependencies into their own relations
        i = 0  # Iterator to name decomposed relations
        if len(partial_dependencies) > 0:
            fd = partial_dependencies[0]
            i += 1
            new_relation = Relation(
                pd.DataFrame(), [], [], [], relation.name + "_" + str(i), []
            )

            for det in fd.determinants:
                new_relation.table[det] = relation.table[det].copy()

            for dep in fd.dependents:
                new_relation.table[dep] = relation.table[dep].copy()
                relation.table.drop(dep, axis=1, inplace=True)

            new_relation.table = new_relation.table.drop_duplicates()

            # Update the key of the new relation
            new_relation.key = fd.determinants

            # Update the FDs of the new relation
            new_relation.FDs = [fd]

            # Remove the FD from the original relation
            relation.FDs.remove(fd)

            # Add the new relation to the list of new relations
            new_relations.append(new_relation)

        # Add the modified original relation to the list of new relations
        new_relations.append(relation)

        # Check if the new relations are in 2NF
        for relation in new_relations:
            if not check_2NF(relation.table, relation.FDs, relation.key):

                new_relations.remove(relation)
                r = transform_to_2NF([relation])
                for i in r:
                    new_relations.append(i)

        return new_relations


def transform_to_3NF(relations: list[Relation]) -> list[Relation]:
    # New list of relations to return
    new_relations = []
    for relation in relations:

        # Check if the relation is in 3NF
        if check_3NF(relation.table, relation.FDs, relation.key):
            new_relations.append(relation)
            continue

        transitive_dependencies = []

        for fd in relation.FDs:
            if fd.determinant != relation.key and fd.dependent not in relation.key:
                transitive_dependencies.append(fd)

        # For every transitive dependency, decompose the table into a new relation
        i = 0  # Iterator to name decomposed relations
        if len(transitive_dependencies) > 0:
            fd = transitive_dependencies[0]
            i += 1
            new_relation = Relation(
                pd.DataFrame(), [], [], [], fd.dependent + "_" + str(i), []
            )

            for determinant in fd.determinants:
                new_relation.table[determinant] = relation.table[determinant].copy()

            for dependent in fd.dependents:
                new_relation.table[dependent] = relation.table[dependent].copy()
                relation.table.drop(columns=dependent, inplace=True)

            new_relation.key = fd.determinants
            new_relation.FDs = [fd]
            new_relation.table = new_relation.table.drop_duplicates()

            # Remove the functional dependency from the original relation
            relation.FDs.remove(fd)

            # Add the new relation to the list of relations
            new_relations.append(new_relation)

        # Add the modified original relation to the list of relations
        new_relations.append(relation)

    # Final Check to make sure all relations are in 3NF
    for relation in new_relations:
        if not check_3NF(relation.table, relation.FDs, relation.key):

            new_relations.remove(relation)
            r = transform_to_3NF([relation])
            for i in r:
                new_relations.append(i)

    return new_relations


def transform_to_BCNF(relations: list[Relation]) -> list[Relation]:
    # New list of relations to return
    new_relations = []
    for relation in relations:

        # Check if the relation is in BCNF
        if check_BCNF(relation.table, relation.FDs, relation.key):
            new_relations.append(relation)
            continue

        violations = []

        # Find all FDs that violate BCNF
        for fd in relation.FDs:
            # For a relationship to be in BCNF, the determinant must be a superkey
            if not is_superkey(relation.table, fd.determinants):
                violations.append(fd)

        # For every violation, decompose the table into two relations R-A and XA
        i = 0  # Iterator to name decomposed relations
        if len(violations) > 0:
            i += 1
            new_relation = Relation(
                pd.DataFrame(), [], [], [], fd.dependent + "_" + str(i), []
            )

            # Add the determinants over to the new relation
            for determinant in fd.determinants:
                new_relation.table[determinant] = relation.table[determinant].copy()

            # Add the dependents over to the new relation and remove them from the original relation
            for dependent in fd.dependents:
                new_relation.table[dependent] = relation.table[dependent].copy()
                relation.table.drop(columns=dependent, inplace=True)

            # Update the key of the new relation
            new_relation.key = fd.determinants

            new_relation.table = new_relation.table.drop_duplicates()
            # Update the FDs of the new relation
            new_relation.FDs = [fd]

            # Add the new relation to the list of new relations
            new_relations.append(new_relation)

            # Remove the FD from the original relation
            relation.FDs.remove(fd)

        # Add the modified original relation to the list of new relations
        new_relations.append(relation)

    # Final Check to make sure all relations are in BCNF
    for relation in new_relations:
        if not check_BCNF(relation.table, relation.FDs, relation.key):

            new_relations.remove(relation)

            # Since new relations were not in BCNF, decompose them further
            r = transform_to_BCNF([relation])
            for i in r:
                new_relations.append(i)

    return new_relations


# Assume the table is in BCNF. Transform it to 4NF
def transform_to_4NF(
    relations: list[Relation], MVDs: list[MultiValuedDependency]
) -> list[Relation]:
    new_relations = []

    # Check to see if any of the original MVDs are still valid
    MVDs = validate_MVDs(relations, MVDs)

    if MVDs == []:
        return relations

    i = 0  # Iterator to name decomposed relations
    for mvd in MVDs:

        relation = find_relation_MVD(relations, mvd)

        # For every non-trivial MVD, if the determinant is a superkey, then it is in 4nf
        if is_superkey(relation.table, mvd.determinants):
            continue

        i += 1

        # Decompose each MVD into a new trivial relation
        for det in mvd.determinants:
            new_relation = Relation(pd.DataFrame(), [], [], [], det + "_" + str(i), [])

            # Add the determinants over to the new relation
            for determinant in mvd.determinants:
                new_relation.table[determinant] = relation.table[determinant].copy()

            # Add the dependents over to the new relation and remove them from the original relation
            for dependent in mvd.dependents:
                new_relation.table[dependent] = relation.table[dependent].copy()
                relation.table.drop(columns=dependent, inplace=True)

            # Update the key of the new relation
            for det in mvd.determinants:
                new_relation.key.append(det)

            for dep in mvd.dependents:
                new_relation.key.append(dep)

            # Add the new relation to the list of new relations
            new_relations.append(new_relation)
            new_relations.table = new_relations.table.drop_duplicates()

        # Add the modified original relation to the list of new relations
        new_relations.append(relation)

        # Remove the relation temporarily to add all the relations together
        relations.remove(relation)

        # Add the remaining relations to the list of new relations
        for r in relations:
            new_relations.append(r)

    return new_relations


# Assume the table is in 4NF. Transform it to 5NF
def transform_to_5NF(
    relations: list[Relation], MVDs: list[MultiValuedDependency]
) -> list[Relation]:
    new_relations = []

    for relation in relations:

        if check_5NF(relation.table, relation.FDs, relation.key):
            new_relations.append(relation)
            continue

    return relations


# Check if initial multivalue dependencies are still valid after decomposition
def validate_MVDs(
    relations: list[Relation], MVDs: list[MultiValuedDependency]
) -> list[MultiValuedDependency]:
    valid_MVDs = MVDs.copy()
    for mvd in valid_MVDs:
        mvd.print()

    for relation in relations:
        for MVD in MVDs:
            valid = True
            group = relation.find_MVD_Determinant(MVD.determinant)
            for i in range(len(group)):
                for j in range(len(group)):
                    if relation.find_relationship(
                        group[i].dependent, group[j].dependent
                    ):
                        valid = False
                        break
            if not valid:
                valid_MVDs.remove(MVD)

    return valid_MVDs


# Find what relation a MVD belongs to
def find_relation_MVD(
    relations: list[Relation], MVD: MultiValuedDependency
) -> Relation:
    for relation in relations:
        if (
            len(relation.find_MVD_Determinant(MVD.determinant)) > 0
            and len(relation.find_MVD_Dependent(MVD.dependent)) > 0
        ):
            return relation

    return None


def update_relationNames(relations: list[Relation]) -> list[Relation]:
    for relation in relations:
        print(relation.name)
        print(relation.table)
        print("Key: ", relation.key)
        print("Functional Dependencies: ")
        for fd in relation.FDs:
            fd.print()

        change_name = input(
            "\nWould you like to change the name of this relation? (y/n): "
        )
        if change_name == "y":
            relation.name = input("Enter the new name: ")
        print()

    return relations


def main():
    pass


if __name__ == "__main__":
    main()

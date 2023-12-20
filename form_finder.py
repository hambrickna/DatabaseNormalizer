import pandas as pd


# Check that the table is in 1NF, meaning there is a proper primary key, and each column must be atomic.  No multi-valued attributes or sets.
def check_1NF(df: pd.DataFrame, key: list[str], mvAttributes: list[str]) -> bool:
    # Check that there are no multivalued attributes
    if mvAttributes is not None:
        return False

    # Check that the primary key columns exist in the table
    for col in key:
        if col not in df.columns:
            return False

    # Check that the primary key is unique and has no null values
    df["combined"] = df[key].apply(lambda row: " ".join(row.values.astype(str)), axis=1)
    is_unique = df["combined"].nunique() == len(df["combined"])
    has_no_null = df[key].notnull().all().all()

    df.drop(columns=["combined"], inplace=True)

    if not is_unique or not has_no_null:
        return False

    # Check that each column contains atomic values
    # Check that all entries in a column are of the same kind
    for name in df.columns:
        data_types = df[name].apply(lambda x: type(x)).unique()
        if len(data_types) > 1 or not data_types[0] in [int, float, str]:
            return False

    return True


# Check that the table is in 2NF, meaning it is in 1NF and every non-prime attribute is fully functionally dependent on the primary key.
def check_2NF(df: pd.DataFrame, FDs, key: list[str]) -> bool:
    if not check_1NF(df, key, None):
        return False

    # Check that every non-prime attribute is fully functionally dependent on the primary key
    for fd in FDs:
        partial = False
        determinant, dependent = fd.determinant, fd.dependent
        determinant = determinant.split(", ")
        dependent = dependent.split(", ")

        # Check for partial dependency with non-prime attribute in dependent
        if determinant != key:
            for det in determinant:
                if det in key:
                    partial = True
            if partial:
                for col in dependent:
                    # If non-prime attribute is in dependent, but determinant doesn't contain all of the key, then partial dependency
                    if col not in key:
                        return False

    return True


# Check that the table is in 3NF, meaning it is in 2NF and every non-prime attribute is non-transitively dependent on the primary key.
def check_3NF(df: pd.DataFrame, FDs: list[str], key: list[str]) -> bool:
    if not check_2NF(df, FDs, key):
        return False

    # Check that every non-prime attribute is non-transitively dependent on the primary key
    for FD in FDs:
        determinant, dependent = FD.determinant, FD.dependent
        determinant = determinant.split(", ")
        dependent = dependent.split(", ")

        # Check for transitive dependency with non-prime attribute in dependent
        if determinant != key:
            # Non-prime attribute
            if dependent not in key:
                if not is_superkey(df, determinant):
                    return False
    return True


# Check that the table is in BCNF, meaning it is in 3NF and every determinant is a superkey
def check_BCNF(df: pd.DataFrame, FDs: list[str], key: list[str]) -> bool:
    if not check_3NF(df, FDs, key):
        return False

    # Check that every determinant is a superkey
    for FD in FDs:
        determinant, dependent = FD.determinant, FD.dependent
        determinant = determinant.split(", ")
        dependent = dependent.split(", ")

        # Check for the determinant being a superkey
        if not is_superkey(df, determinant):
            return False
    return True


# Check that the table is in 4NF, meaning it is in BCNF and for every non-trivial multivalued dependency X ->> Y, X is a superkey
def check_4NF(
    df: pd.DataFrame, FDs: list[str], MVFDs: list[str], key: list[str]
) -> bool:
    if not check_BCNF(df, FDs, key):
        return False

    # Check for multivalued dependencies
    for FD in MVFDs:
        determinant, dependent = FD.determinant, FD.dependent
        determinant = determinant.split(", ")
        dependent = dependent.split(", ")

        # Check determinant of multivalued dependency is a superkey
        if not is_superkey(df, determinant):
            return False

    return True


# Check that the table is in 5NF, meaning it is in 4NF and for every non-trivial join dependency the intersection of the candidate keys of the relations contains a superky of R
def check_5NF(
    df: pd.DataFrame, FDs: list[str], MVDs: list[str], key: list[str]
) -> bool:
    if not check_4NF(df, FDs, MVDs, key):
        return False

    # Check that for every non-trivial join dependency the intersection of the candidate keys of the relations contains a superky of R
    attributes = set(df.columns)

    for attribute in attributes:
        remaining_attributes = attributes - set([attribute])
        if not find_closure(df, attributes, remaining_attributes) == attributes:
            return False

    return True


def is_superkey(df: pd.DataFrame, determinant: list[str]) -> bool:
    df["combined"] = df[determinant].apply(
        lambda row: " ".join(row.values.astype(str)), axis=1
    )
    is_unique = df["combined"].nunique() == len(df["combined"])
    df.drop(columns=["combined"], inplace=True)

    if is_unique:
        return True
    else:
        return False


def find_closure(df, attributes, candidate):
    closure = set(candidate)
    changed = True
    while changed:
        changed = False
        for FD in attributes:
            determinant, dependent = FD.determinant, FD.dependent
            determinant = determinant.split(", ")
            dependent = dependent.split(", ")
            if set(determinant).issubset(closure) and not set(dependent).issubset(
                closure
            ):
                closure = closure.union(set(dependent))
                changed = True

    return closure


# Main function for testing
def main():

    pass


if __name__ == "__main__":
    main()

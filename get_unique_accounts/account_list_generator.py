import pandas as pd
import os
import logging
import logging.config
import yaml

def setup_logging(default_path='../logging_config.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

# Set up logging using the configuration file
setup_logging()

# Create a logger variable
logger = logging.getLogger(__name__)


def assert_file_extension(
        file_name,
        expected_extension: str = '.xlsx',
):
    file_extension=os.path.splitext(file_name)[1]
    try:
        assert (file_extension == expected_extension), (
            f"Incorrect file extension, expecting '{expected_extension}' but got '{file_extension}'"
        )
        return True        
    except AssertionError as e:
        print(f"AssertionError: {e}")
        raise AssertionError(f"AssertionError: {e}")

def read_file(file_name):
    xls = pd.ExcelFile(file_name)
    sheet_names = xls.sheet_names
    print(f"Account Listings: {sheet_names}")
    
    return xls, sheet_names

def read_sheets_as_df(xls):
    # Get Sheet Names
    sheet_names = xls.sheet_names

    # Read each sheet into a DataFrame
    account_list_dfs_dict = {}
    for sheet_name in sheet_names:
        account_list_dfs_dict[sheet_name] = xls.parse(sheet_name)

    return account_list_dfs_dict

def basic_checks_acc_gen(
        account_list_dfs_dict
):
    # Pass unless fails
    pass_checks=True

    for account_listing in account_list_dfs_dict.keys():
        # All dfs must only have 1 column
        if not (account_list_dfs_dict[account_listing].shape[1] == 1):
            logger.info(f'ERROR: account_listing:{account_listing} contains more than one column, please review.')
            pass_checks=False

        # All values in the df must be unique
        if not (len(account_list_dfs_dict[account_listing].iloc[:, 0].unique()) == len(account_list_dfs_dict[account_listing].iloc[:, 0])):
            logger.info(f'ERROR: account_listing:{account_listing} contains duplicate values, please review.')
            pass_checks=False

    if pass_checks:
        logger.debug("All checks have passes.")
        return True
    else:
        logger.info('ERROR - please review above errors.')
        return False

def get_list_of_unique_accounts(
        account_list_dfs_dict
):
    # Convert to lists
    account_lists_dict = {}
    all_accounts = []
    for account_listing in account_list_dfs_dict.keys():
        new_list=list(account_list_dfs_dict[account_listing].iloc[:,0])
        account_lists_dict[account_listing]=new_list
        all_accounts=all_accounts+new_list

    return account_lists_dict, list(set(all_accounts))

def generate_check_account_order_dict(
        account_lists_dict,
        unique_accounts_list
):
    # Make a dictionary that details all accounts expected before and after another account
    check_account_order_dict = {}
    for account in unique_accounts_list:
        check_account_order_dict[account] = {
            'before': [],
            'after': [],
        }

    for account_listing in account_lists_dict.keys():
        current_list=account_lists_dict[account_listing]

        for account in current_list:
            # Find the index of the specific value
            index_of_account = current_list.index(account)

            # Get all values before the specific value
            accounts_before = current_list[:index_of_account]

            # Update before list
            check_account_order_dict[account]['before'] = list(set(
                check_account_order_dict[account]['before'] +
                accounts_before,
            ))

            # Get all values after the specific value
            accounts_after = current_list[index_of_account + 1:]

            # Update after list
            check_account_order_dict[account]['after'] = list(set(
                check_account_order_dict[account]['after'] +
                accounts_after
            ))

    return check_account_order_dict

def exclusive_list_check(list_1, list_2, detail):
    pass_checks=True
    # print(f'{detail} listing (List 1):{list_1}')
    # print(f'Should not be in (List 2):{list_2}')
    for item in list_1:
        if item in list_2:
            logger.info(f'{item} is incorrectly {detail} these values {list_2}')
            pass_checks = False

    return pass_checks

def account_order_checker(
        check_account_order_dict,
        account_list,
):
    for account in account_list:
        pass_checks=True
        # print(f'\n\n\nchecking:{account}')
        # Find the index of the specific value
        index_of_account = account_list.index(account)

        # Get all values before the specific value
        accounts_before = account_list[:index_of_account]
        # print(f'\nBefore list: {accounts_before}')

        # Make sure values in before list shouldnt be in the after list
        if not exclusive_list_check(list_1 = accounts_before, list_2 = check_account_order_dict[account]['after'], detail = 'before'):
                pass_checks=False

        # Get all values after the specific value
        accounts_after = account_list[index_of_account + 1:]
        # print(f'\nAfter list: {accounts_after}')

        # Make sure values in the after lsit shouldnt be in the before list
        if not exclusive_list_check(list_1 = accounts_after, list_2 = check_account_order_dict[account]['before'], detail = 'after'):
                pass_checks=True
        
        if not pass_checks:
                logger.info('This list fails the checks\n\n\n')

        return(pass_checks)

def complete_account_order_checker(
        check_account_order_dict,
        account_list_lists,
):
    # Passes unless failure
    pass_checks = True

    for account_list in account_list_lists:
        if not account_order_checker(
            check_account_order_dict=check_account_order_dict,
            account_list=account_list_lists[account_list],
        ):
            pass_checks=False
    
    return pass_checks

def correctly_ordered_list(
        check_account_order_dict,
):
    ordered_account_list = []
    for accoount in check_account_order_dict.keys():
        # print(f'\n\nAssessing:{accoount}')
        # check_account_order_dict[key]

        before_list = check_account_order_dict[accoount]['before']
        # print(before_list)
        max_before_pos=None
        for item in before_list:
            if (item in ordered_account_list):
                pos=ordered_account_list.index(item)
                if max_before_pos == None:
                    max_before_pos = pos
                elif pos > max_before_pos:
                    max_before_pos = pos
        # print(f'max_before_pos:{max_before_pos}')

        after_list = check_account_order_dict[accoount]['after']
        # print(after_list)
        min_after_pos=None
        for item in after_list:
            if (item in ordered_account_list):
                pos=ordered_account_list.index(item)
                if min_after_pos == None:
                    min_after_pos = pos
                elif pos < min_after_pos:
                    min_after_pos=pos
        # print(f'min_after_pos:{min_after_pos}')

        if (max_before_pos == None) and (min_after_pos == None):
            ordered_account_list = ordered_account_list + [accoount]
            # print("Nones")
            # print(ordered_account_list)
        elif max_before_pos == None:
            # print(f'min_after_pos:{min_after_pos}')
            # Add after the last item it needs to be before
            ordered_account_list.insert(min_after_pos, accoount)
            # print(ordered_account_list)
        else:
            # print("No after position indicator")
            # print(f'max_before_pos:{max_before_pos}')
            # max_before_pos is not None, insert one before max_before_pos
            ordered_account_list.insert(max_before_pos+1, accoount)
            # print(ordered_account_list)
            

    return ordered_account_list

def main(
        file_name: str = "account_lists_single_tst.xlsx",
):
    logger.info('Main file running')

    # Check file is Excel
    assert_file_extension(file_name, expected_extension='.xlsx')

    # Read the Excel file
    xls = pd.ExcelFile(file_name)

    # Read in sheets as dfs
    account_list_dfs_dict = read_sheets_as_df(xls)
    
    # Run basic account list checks
    assert (basic_checks_acc_gen(account_list_dfs_dict=account_list_dfs_dict)), ('Basic checks have failed')

    # Get a list of unique accounts from all lists
    account_lists_dict, unique_accounts_list=get_list_of_unique_accounts(account_list_dfs_dict)

    # Create a dictionary to use as account ofer checker
    check_account_order_dict=generate_check_account_order_dict(account_lists_dict, unique_accounts_list)

    # Check all account lists are in the expected order
    assert complete_account_order_checker(
            check_account_order_dict,
            account_lists_dict,
    ), 'Some accounts are not in the correctr order, please review'

    # At this point you have a list of acount lists
    # These account lists are all in the correct order

    ordered_account_list = correctly_ordered_list(check_account_order_dict)

    return ordered_account_list # eventually return the base list.

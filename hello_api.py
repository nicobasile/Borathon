from flask import Flask, request, jsonify, render_template
from enum import IntEnum
import uuid

app = Flask(__name__)

accounts = {} # map AccountNumber : Account object
customers = {} # map AccountNumber to customer object

# Accounts
class AccountStatus(IntEnum):
    OPEN = True
    CLOSED = False

class Account:
    def __init__(self, ID):
        self.ID = ID # Assigned with account creation/customer's ID
        self.AccountNumber = str(uuid.uuid4()) # Generate a random unique ID for Acc # 
        self.Balance = 0.0
        self.AccountStatus = AccountStatus.OPEN # True for OPEN, False for Closed
  
# Customers
class Customer:
    ID = 0 # Static variable to increment ID
    def __init__(self, firstName, lastName):
        Customer.ID += 1 # Increment itself on each creation
        self.ID = Customer.ID
        self.firstName = firstName
        self.lastName = lastName
        self.AssociatedAccount = ""

# Transactions
class Transaction:
    def __init__(self, accountNumber, transactionAmount, transactionType):
        # self.ID = new id ; we can match account based on account number and set the ID there
        self.Amount = transactionAmount
        self.Type = transactionType # Debit or Credit
        self.AssociatedAccount = accountNumber # Foreign key relationship
    

@app.route('/')
def get_root():
    print('sending root')
    return render_template('index.html')

@app.route('/api/docs')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')

@app.route('/api/OpenCustomerAccount', methods=['POST'])
def openCustomerAccount():
    body = request.get_json()
    if 'firstName' not in body or 'lastName' not in body:
        return jsonify({'statusCode': 400, 'Description': 'Invalid input of first/last name'})

    firstName, lastName = body['firstName'], body['lastName']
    customer = Customer(firstName, lastName)
    account = Account(customer.ID)
    if account.AccountNumber not in accounts:
        accounts[account.AccountNumber] = account
        customer.AssociatedAccount = account.AccountNumber
        customers[account.AccountNumber] = customer
    return jsonify(formatOpenedAccountResponse(customer, account))

def formatOpenedAccountResponse(customer, account):
    return {
        'values': {
            'id': customer.ID,
            'firstName': customer.firstName,
            'lastName': customer.lastName,
            'account': {
                'id': account.ID,
                'accountNumber': account.AccountNumber,
                'balance': account.Balance,
                'status': account.AccountStatus
            }
        },
        'statusCode': 200
    }
  
  
@app.route('/api/ApplyTransactionToCustomerAccountAsync', methods=['POST'])
def applyTransaction():
    body = request.get_json()
    if 'accountNumber' not in body or 'amount' not in body or 'transactionType' not in body:
        return jsonify({'statusCode': 400, 'Description': 'Invalid input of accountNumber/amount/transactionType'})

    accountNumber, amount, transactionType = body['accountNumber'], body['amount'], body['transactionType']

    #transaction type 1 == credit, 0 == debit
    account = accounts[accountNumber]
    
    if account.AccountStatus == account.AccountStatus.CLOSED:
      return jsonify({'statusCode': 400, 'Description': 'Bank account has been closed'})

    if (transactionType == 1):
        account.Balance += amount
    elif (transactionType == 0):
        if account.Balance - amount <= 0:
            return jsonify({'statusCode': 400, 'Description': 'Insuffucient balance' })
        else:
            account.Balance -= amount
    else:
        return jsonify({'statusCode': 400, 'Description': 'Invalid transaction type, must be 0 for debit or 1 for credit' })

    accounts[accountNumber] = account

    return jsonify(formatApplyTransactionResponse(account))


def formatApplyTransactionResponse(account):
    customer = customers[account.AccountNumber]
    return {
        'value': {
            'id': customer.ID,
            'firstName': customer.firstName,
            'lastName': customer.lastName,
            'account': {
                'id': account.ID,
                'accountNumber': account.AccountNumber,
                'balance': account.Balance,
                'status': account.AccountStatus
            },
            "accountId": account.ID
        },
        'statusCode': 200
    }

@app.route('/api/CustomerDetails', methods=['GET'])
def get_customer_details():
    acc_number = request.args.get('accnumber')
    if acc_number in customers:
        customer = customers[acc_number]
        return 'First Name: ' + customer.firstName + ' Last Name: ' + customer.lastName + ' Associated Account = ' + customer.AssociatedAccount + '\nBalance = ' + str(accounts[customer.AssociatedAccount].Balance)
    else:
        return 'No customer with that Account Number' + acc_number
      
@app.route('/api/CloseAccount', methods=['POST'])
def close_account():
    acc_number = request.args.get('accnumber')
    if acc_number in accounts:
        account = accounts[acc_number]
        account.AccountStatus = AccountStatus.CLOSED
        accounts[acc_number] = account
        return 'Closed account number: ' + acc_number
    else:
        return 'No account with that Account Number: ' + acc_number

app.run(use_reloader=True, debug=True)
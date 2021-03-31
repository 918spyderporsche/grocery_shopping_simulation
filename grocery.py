from collections import defaultdict
import sys, getopt

'''
Global variables
'''
NUM_REGISTERS = 0
customers = {}
registers = []
times = defaultdict(list)

'''
Customer class
'''
class Customer:

    '''
    Constructor for a Customer object
    type_: "A" or "B"
    arrival_: time of arrival of customer
    items_: the # of merchandise the customer has
    name: the key of the object
    '''
    def __init__(self, type_, arrival_, items_):
        self.type_ = type_
        self.arrival_ = arrival_
        self.items_ = items_
        self.name = id(self)

    '''
    choose() method:
    Customer picks the best register given their type and current states of registers at the current time, and queues up in front of the chosen register, and changes the register's state to not open.
    If type 'A', customer picks register with shortest line. If lines have same lengths, pick the lowest numbered register
    If type 'B', customer picks register whose last member in line has fewest number of items; if there is an empty register, customer would pick it. Lowest number register takes priority
    '''
    def choose(self):
        sorted_regs = []
        if (self.type_ == 'A'):  
            sorted_regs = sorted(registers, key = lambda reg : (len(reg.queue_), reg.index_))
        else:
            empty_regs = [reg for reg in registers if reg.open_ == 1]
            if not empty_regs:
                sorted_regs = sorted(registers, key = lambda reg : (reg.queue_[-1].items_, reg.index_))
            else:
                sorted_regs = sorted(empty_regs, key = lambda reg : reg.index_)
        best_reg = sorted_regs[0]
        best_reg.queue_.append(self)
        if (best_reg.open_):
            best_reg.open_ = 0
            best_reg.customer_ = self

'''
Register class
'''
class Register:
    '''
    Register constructor.
    index_: index of register
    training_: whether it is a training register
    open_: whether the register is open to receive the next customer
    queue_: queue of customers that is waiting at the register
    customer_: current customer the register is serving
    '''
    def __init__(self, index_, training_):
        self.open_ = 1
        self.queue_ = [] 
        self.index_ = index_
        self.training_ = training_
        self.customer_ = None
    
    '''
    serve()
    serves the current customer for one minute. 
    if there is no customer, it stays idle.
    serve() always happens after schedule(), so it
    assumes that customers are readily scheduled and arranged.
    '''
    def serve(self):
        if (self.open_): return

        speed = 1 if not self.training_ else 0.5
        minute = 1
        # proceed with current customer
        self.customer_.items_ -= speed * minute
        if (self.customer_.items_ == 0):
            # done with this customer
            self.queue_.pop(0)
            customers.pop(self.customer_.name, None)
            if (len(self.queue_) > 0):
                self.customer_ = self.queue_[0]
            else:
                self.customer_ = None
                self.open_ = 1

'''
order people who arrive at the same time
'''
def order(people):
    people.sort(key = lambda person : (person.items_, person.type_))

'''
schedules customers whose arrivals are 'time' to cashiers
'''
def schedule(times, time):
    if time not in times:
        return
    people = times[time]
    order(people)
    for person in people:
        person.choose()

'''
all registers proceed to serve the current customer in their queues
'''
def all_registers_proceed():
    for reg in registers:
        reg.serve()
'''
main function that takes input from input file, parses it and initializes everything
'''
def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print('python grocery.py -i <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print('python grocery.py -i <inputfile>')
          sys.exit()
       elif opt in ("-i", "--ifile"):
          inputfile = arg
    if inputfile == '':
        print('python grocery.py -i <inputfile>')
        sys.exit(2)
    data = ""
    with open(inputfile, "r") as f:
        data = f.read()
    
    data = data.split('\n')
    new_input = [int(data[0])]
    for elem in data[1:]:
        if elem == '': continue
        type_, arrival_, items_ = elem.split(' ')
        new_input.append([type_, int(arrival_), int(items_)])
    
    input_ = new_input
    NUM_REGISTERS = input_[0]
    for line in input_[1:]:
        type_, arrival_, items_ = line
        cur_customer = Customer(type_, int(arrival_), int(items_))
        customers[cur_customer.name] = cur_customer
    for name in customers.keys():
        times[customers[name].arrival_].append(customers[name])
    for i in range(NUM_REGISTERS - 1):
        register = Register(i + 1, 0)
        registers.append(register)
    registers.append(Register(NUM_REGISTERS, 1))     # add the training reg
    # start simulation
    time = 0
    while len(customers.keys()) > 0:
        # schedule customers
        schedule(times, time)
        # start checking out
        all_registers_proceed()
        time += 1

    print("Finished at: t=%d minutes" % time)
    return 0

if __name__ == "__main__":
   main(sys.argv[1:])


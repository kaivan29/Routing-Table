from socket import *
import sys


# Test script for Project 2
# This code is pretty brain dead. It doesn't catch exceptions if things crash,
# but does check responses to see if they are correct


# First a bunch of helpers. Skip to the end to see the actual tests sent


# A function that checks the ACK that comes back to make sure it is
# properly formed
# Returns True if properly formed, False if not
# Used by sendUpdate below
def checkAck(responseMsg):

    # Make sure length is right.
    # Should always be 10 chars: ACK<cr><lf>END<cr><lf>
    if (len(responseMsg) != 10):
        print('...............Length is wrong.')
        return False

    # split the message into chunks at the crlf boundaries - should be three
    # chunks, the two real lines plus "empty" after the final crlf
    lines = responseMsg.split('\r\n')
    if (len(lines) != 3):
        print('...............Linecount is wrong.')
        return False
    
    # make sure the first line is ACK and second is END
    if ((lines[0] != 'ACK') or (lines[1] != 'END')):
        print('...............Ack didn\'t contain ACK and END')
        return False

    return True




# A function that checks that the RESULT that comes back for a
# query is properly formed
# Returns four things -- (Status, IP, AS, and cost)
# Status is False if the response is malformed, IP/AS set to NULL and cost to -1
# IP, AS and cost are extracted from the response if response is not malformed
# Used by sendQuery below
def checkResponse(responseMsg):

    # split the message into chunks at the crlf boundaries
    # should be four chunks, the three real lines (RESULT, the answer,
    # END, plus "empty" after the final crlf
    lines = responseMsg.split('\r\n')
    if (len(lines) != 4):
        print('...............Linecount is wrong.')
        return (False, 'NULL', 'NULL', -1)
    
    # make sure the first line is ACK and third is END
    if ((lines[0] != 'RESULT') or (lines[2] != 'END')):
        print('...............Response didn\'t contain RESULT and END')
        return (False, 'NULL', 'NULL', -1)

    # split answer line in three -- IP, AS, and cost -- with spaces
    # make sure there are 3 parts, but otherwise we don't check here
    parts = lines[1].split(' ')
    if (len(parts) != 3):
        print('...............Wrong number of items in answer line.')
        return (False, 'NULL', 'NULL', -1)

    # if it works, return what should be IP, AS, and cost (the three parts)
    return (True, parts[0], parts[1], int(parts[2]))





# A helper function to make and send an UPDATE message, given a "body"
# The string passed in as "body" is not checked so make sure it is right
# Look at the ACK received to make sure it is a valid
# Returns True if a valid ACK is received, False otherwise
def sendUpdate(updateBody):

    # open socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))

    # format message
    completeMsg = 'UPDATE\r\n'
    completeMsg += updateBody # Just stuff in whatever we get
    completeMsg += 'END\r\n'

    # check response and return results, close socket
    clientSocket.send(completeMsg.encode())
    response = clientSocket.recv(2048)
    clientSocket.close()

    # check and return results
    success = checkAck(response.decode())
    return success
        




# A helper function to make and send a QUERY message, given an IP address
# searchFor that is used for the query
# The string searchFor is simply passed and not checked so make sure it is right
# Look at the RESULT received to make sure it is a valid and extract result
# Returns four things -- (Status, IP, AS, and cost)
# Status is False if the response is malformed, IP/AS set to NULL and cost to -1
# IP, AS and cost are extracted from the response if response is not malformed
def sendQuery(searchFor):

    # open socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))

    #format message
    completeMsg = 'QUERY\r\n'
    completeMsg += searchFor
    completeMsg += '\r\n'
    completeMsg += 'END\r\n'

    # send message, get response, close socket
    clientSocket.send(completeMsg.encode())
    response = clientSocket.recv(2048)
    clientSocket.close()
    
    # check and return results
    (success, IP, AS, cost) = checkResponse(response.decode())
    return (success, IP, AS, cost)







# Helper to run a query test and print the result nicely
# Takes IP to query, and expected AS/cost to verify
def queryHelper (exIP, exAS, exCost):

    global testID
    global testsPassed
    
    testStr = "%03d" % testID 
    
    print ('Test ' + testStr + ' (Query ' + exIP + '): Expecting ' + exAS +
           ' @ cost ' + str(exCost))
    
    (success, IP, AS, cost) = sendQuery(exIP)
    if (success == False):
        print('...............FAILED (malformed response)\n')
    else:
        if (AS == exAS and cost == exCost and IP == exIP):
            print('...............SUCCESS\n')
            testsPassed += 1
        else:
            # message worked but wrong answer
            if (AS != exAS or cost != exCost or IP != exIP):
                print('...............FAILED (AS should be ' + exAS +
                      ' with cost ' + str(exCost) + ' for IP ' + exIP + ')')
                print('...............       (Instead got  ' + AS +
                      ' with cost ' + str(cost) + ' for IP ' + IP + ')\n')
            else:
                print('...............FAILED (Unknown error)\n')

    testID += 1
    return





                
# Helper to run a query test and print the result nicely
# Takes a body that must already be formed correctly. Should have a nice
# helper to build that but not here now...
def updateHelper (updateBody):

    global testID
    global testsPassed

    testStr = "%03d" % testID 
    
    print ('Test ' + testStr + ' (Update): Expecting ACK')

    success = sendUpdate(updateBody)

    if (success == False):
        print('...............FAILED (malformed response)\n')
    else:
        print('...............SUCCESS\n')
        testsPassed += 1

    testID += 1
    return

                




# Main program

# global variables for host and port of server, ugly but easy
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

# global also for test ID and array of results
testID = 0
testsPassed = 0


# Run the tests


# query first, no routes. Should give A at weight 100
queryHelper('192.168.2.100','A', 100)


# now update with a few /24 routes for B 
body = 'B 200.55.1.0/24 50\r\n'
body += 'B 200.55.2.0/24 50\r\n'
body += 'B 200.55.3.0/24 50\r\n'
updateHelper(body)


# now update with a few /24 routes for C and D in same message 
body = 'C 200.55.4.0/24 40\r\n'
body += 'D 200.55.5.0/24 40\r\n'
body += 'D 200.55.6.0/24 40\r\n'
updateHelper(body)

    
# query again, even with new routes should give A at weight 100
queryHelper('192.168.2.100','A', 100)

# query new route. Should give B at weight 50
queryHelper('200.55.1.40','B', 50)

# query new route. Should give D at weight 50
queryHelper('200.55.6.40','D', 40)

# query new route not claimed in any UPDATE. Should give A at weight 100
queryHelper('200.55.8.40','A', 100)


# now update with a /16 routes for E that is more expensive (so won't override
# the cheaper /24s, but does cover other 200.55.*.*) 
updateHelper('E 200.55.0.0/16 75\r\n')


# query route again. Should still give D at weight 50
queryHelper('200.55.6.40','D', 40)

# query route again. Should now give E at weight 75, not A
queryHelper('200.55.8.40','E', 75)

perc = testsPassed/testID * 100

print('SUMMARY: ' + str(testsPassed) + ' of ' + str(testID) + ' (' + str(perc) + '%) tests passed.\n\n')

# That's it...
            

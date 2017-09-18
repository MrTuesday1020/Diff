import re
from itertools import product

class DiffCommands:
    def __init__(self,filename):
        with open(filename) as f:
            lines = f.read().splitlines()
        self.lines = lines[:]
        
        self.diff = ''
        for i in range(len(lines)-1):
            self.diff += lines[i] + '\n'
        self.diff += lines[-1]
        
        for line in lines:
            # for wrong_3
            if line == '':
                raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
            else:
                for item in line:
                    # for wrong_1,2
                    if not (item.isdigit() or item in 'adc,'):
                        raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')

        commands = []
        for i in range(len(lines)):
            command = []
            # delete
            delete = re.match("^(\d+)(?:,(\d+))?d(\d+)$",lines[i])
            # add
            add = re.match("^(\d+)a(\d+)(?:,(\d+))?$",lines[i])
            # change
            change = re.match("^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$",lines[i])
            if delete == None and add == None and change == None:
                # for wrong_4
                raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
            elif delete != None:
                # for wrong_5
                if delete.groups()[0] == '1' and delete.groups()[2] != '0':
                    raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                else:
                    if delete.groups()[1] == None:
                        former = (int(delete.groups()[0]),int(delete.groups()[0]))
                    else:
                        former = (int(delete.groups()[0]),int(delete.groups()[1]))
                    latter = ((int(delete.groups()[2])+1),int(delete.groups()[2]))
                    command = ('d',former,latter)
                    commands.append(command)
            elif add != None:
                former = (int(add.groups()[0]),int(add.groups()[0]))
                if add.groups()[2] == None:
                    latter = (int(add.groups()[1]),int(add.groups()[1]))
                else:
                    latter = (int(add.groups()[1]),int(add.groups()[2]))
                command = ('a',former,latter)
                commands.append(command)
            elif change != None:
                if change.groups()[1] == None:
                    former = (int(change.groups()[0]),int(change.groups()[0]))
                else:
                    former = (int(change.groups()[0]),int(change.groups()[1]))
                if change.groups()[3] == None:
                    latter = (int(change.groups()[2]),int(change.groups()[2]))
                else:
                    latter = (int(change.groups()[2]),int(change.groups()[3]))
                command = ('c',former,latter)
                commands.append(command)
        
        for i in range(len(commands)-1):
            difference1 = commands[i+1][1][0] - commands[i][1][1]
            difference2 = commands[i+1][2][0] - commands[i][2][1]
            # for wrong_6
            if difference1 == 1 and difference2 == 1:
                raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
            # for wrong_7
            if difference1 > difference2:
                raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
        self.commands = commands[:]

    def __str__(self):
        return self.diff

class DiffCommandsError(Exception):
    def __init__(self, message):
        self.message = message

class OriginalNewFiles:
    def __init__(self, filename1, filename2):
        with open(filename1) as f:
            lines1 = f.read().splitlines()
        self.file1 = lines1
        with open(filename2) as f:
            lines2 = f.read().splitlines()
        self.file2 = lines2

    def is_a_possible_diff(self,diff):
        self.get_all_diff_commands()
        return diff.lines in self.final_diffs

    def output_diff(self, diff):
        output = ''
        for i in range(len(diff.commands)):
            if i == 0:
                output += diff.lines[i]
            else:
                output += '\n' + diff.lines[i]
            if diff.commands[i][0] == 'd':
                start1 = diff.commands[i][1][0] - 1
                end1 = diff.commands[i][1][1]
                for j in range(start1, end1):
                    output += '\n' + '< ' + self.file1[j]
            if diff.commands[i][0] == 'a':
                start2 = diff.commands[i][2][0] - 1
                end2 = diff.commands[i][2][1]
                for j in range(start2, end2):
                    output += '\n' + '> ' + self.file2[j]
            if diff.commands[i][0] == 'c':
                start1 = diff.commands[i][1][0] - 1
                end1 = diff.commands[i][1][1]
                start2 = diff.commands[i][2][0] - 1
                end2 = diff.commands[i][2][1]
                for j in range(start1, end1):
                    output += '\n' + '< ' + self.file1[j]
                output += '\n' + '---'
                for j in range(start2, end2):
                    output += '\n' + '> ' + self.file2[j]
        print(output)

    def output_unmodified_from_original(self, diff):
        period = []
        for i in range(len(self.file1)):
            period.append(i)
        for i in range(len(diff.commands)):
            if diff.commands[i][0] != 'a':
                period[diff.commands[i][1][0]-1] = '...'
                for j in range(diff.commands[i][1][0], diff.commands[i][1][1]):
                    period[j] = None
        period = [x for x in period if x != None]
        output = ''
        for i in range(len(period)):
            if i != 0:
                output += '\n'
            if period[i] != '...':
                output += self.file1[period[i]]
            else:
                output += '...'
        print(output)

    def output_unmodified_from_new(self, diff):
        period = []
        for i in range(len(self.file2)):
            period.append(i)
        for i in range(len(diff.commands)):
            if diff.commands[i][0] != 'd':
                period[diff.commands[i][2][0]-1] = '...'
                for j in range(diff.commands[i][2][0], diff.commands[i][2][1]):
                    period[j] = None
        period = [x for x in period if x != None]
        output = ''
        for i in range(len(period)):
            if i != 0:
                output += '\n'
            if period[i] != '...':
                output += self.file2[period[i]]
            else:
                output += '...'
        print(output)

    def get_all_diff_commands(self):
        lcs_list = self.lcs_mat()
        diff_list = []
        while len(lcs_list) > 0:
            now_list = [lcs_list[0]]
            for i in range(1,len(lcs_list)):
                if lcs_list[0][0] == lcs_list[i][0] or lcs_list[0][1] == lcs_list[i][1]:
                    now_list.append(lcs_list[i])
            lcs_list = [item for item in lcs_list if item not in now_list]
            diff_list.append(now_list)
        diff_list = list(product(*diff_list))
        for i in range(len(diff_list)):
            for j in range(len(diff_list[i])-1):
                if diff_list[i][j][1] >= diff_list[i][j+1][1] or diff_list[i][j][0] >= diff_list[i][j+1][0]:
                    diff_list[i] = None
                    break
        diff_list = [l for l in diff_list if l != None]
        diff_list = [([0,0],) + l for l in diff_list]
        diff_list = [l + ([len(self.file1)+1,len(self.file2)+1],) for l in diff_list]
        final_diffs = []
        for i in diff_list:
            sub_final_diff = []
            for j in range(len(i)-1):
                distance1 = i[j+1][0]- i[j][0]
                distance2 = i[j+1][1]- i[j][1]
                if distance1 == 1 and distance2 > 1:
                    #add
                    left = i[j][0]
                    right1 = i[j][1] + 1
                    right2 = i[j+1][1] - 1
                    if right1 == right2:
                        diff_line = str(left) + 'a' + str(right1)
                    else:
                        diff_line = str(left) + 'a' + str(right1) + ',' + str(right2)
                    sub_final_diff.append(diff_line)
                if distance1 > 1 and distance2 == 1:
                    #delete
                    left1 = i[j][0] + 1
                    left2 = i[j+1][0] - 1
                    right = i[j][1]
                    if left1 == left2:
                        diff_line = str(left1) + 'd' + str(right)
                    else:
                        diff_line = str(left1) + ',' + str(left2) + 'd' + str(right)
                    sub_final_diff.append(diff_line)
                if distance1 > 1 and distance2 > 1:
                    #change
                    left1 = i[j][0] + 1
                    left2 = i[j+1][0] - 1
                    right1 = i[j][1] + 1
                    right2 = i[j+1][1] - 1
                    if left1 == left2 and right1 == right2:
                        diff_line = str(left1) + 'c' + str(right1)
                    if left1 != left2 and right1 == right2:
                        diff_line = str(left1) + ',' + str(left2) + 'c' + str(right1)
                    if left1 == left2 and right1 != right2:
                        diff_line = str(left1) + 'c' + str(right1) + ',' + str(right2)
                    if left1 != left2 and right1 != right2:
                        diff_line = str(left1) + ',' + str(left2) + 'c' + str(right1) + ',' + str(right2)
                    sub_final_diff.append(diff_line)
            final_diffs.append(sub_final_diff)
        final_diffs_string = []
        for diff in final_diffs:
            diff_string = ''
            for i in range(len(diff)):
                if i == 0:
                    diff_string += diff[i]
                else:
                    diff_string += '\n' + diff[i]
            final_diffs_string.append(diff_string)
        self.final_diffs_string = final_diffs_string
        self.final_diffs = final_diffs
        final_diffs_string = sorted(final_diffs_string)
        return final_diffs_string


    def lcs_mat(self):
        list1 = self.file1[:]
        list2 = self.file2[:]
        m = len(list1)
        n = len(list2)
        # construct the matrix, of all zeroes
        mat = [[0] * (n+1) for row in range(m+1)]
        # populate the matrix, iteratively
        lcs_list = []
        for row in range(1, m+1):
            for col in range(1, n+1):
                if list1[row - 1] == list2[col - 1]:
                    # if it's the same element, it's one longer than the LCS of the truncated lists
                    mat[row][col] = mat[row - 1][col - 1] + 1
                    lcs_list.append([row, col])
                else:
                    # they're not the same, so it's the the maximum of the lengths of the LCSs of the two options (different list truncated in each case)
                    mat[row][col] = max(mat[row][col - 1], mat[row - 1][col])
        # the matrix is complete
        return lcs_list

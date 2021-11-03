# general_file = 'Tong hop BC phat hanh 2020-2021_HCM.xlsx'
# detail_file = 'NV6A_Kiem toan.xlsx'

import os
import pandas as pd

file = list()

for f in os.listdir():
    if f.endswith(".xlsx"): file.append(f)

if len(file) > 2:
    raise Exception("More than 2 file detected!")

if os.path.getsize(file[0]) > os.path.getsize(file[1]):

    general_file = file[0]
    detail_file = file[1]
    print("General file: {file} ({size} byte)".format(file=file[0], size=os.path.getsize(file[0])))
    print("Detail file: {file} ({size} byte)".format(file=file[1], size=os.path.getsize(file[1])))

elif os.path.getsize(file[0]) < os.path.getsize(file[1]):

    general_file = file[1]
    detail_file = file[0]
    print("General file: {file} ({size} byte)".format(file=file[1], size=os.path.getsize(file[1])))
    print("Detail file: {file} ({size} byte)".format(file=file[0], size=os.path.getsize(file[0])))

general = pd.read_excel(general_file, header=2, index_col=0, sheet_name = 'BCKT_cap nhat')
general = general.dropna(thresh=3)
general = general.fillna("Không có")

detail = pd.read_excel(detail_file, header=5, index_col=0)
detail = detail.dropna(thresh=1)
detail = detail.fillna("Không có")

columns = ["Số báo cáo", "Ngày phát hành", "Ghi chú", "Loại báo cáo", "Nghiệp vụ", "Khách hàng (chữ in hoa như trong BC)", "Nội dung báo cáo", "Kiểm toán viên", "Partner", "Loại hình công ty", "Loại ý kiến"]

def write_file(content):
    file = open('ketqua.txt', 'a')
    file.write(content)
    file.close()

def format_client_name(client_list):

    result = list()

    for i in range(len(client_list)):

        if client_list[i][:3] == 'CTY':
            client_list[i] = client_list[i].replace('CTY', 'CÔNG TY')
            result.append(client_list[i])
        elif client_list[i][8:10] == 'CP':
            client_list[i] = client_list[i].replace('CP', 'CỔ PHẦN')
            result.append(client_list[i])

        else: result.append(client_list[i])

    return result

def format_note(note_list):

    result = list()

    for i in range(len(note_list)):

        if isinstance(note_list[i], str): result.append(note_list[i].capitalize())
        else: result.append(note_list[i])

    return result

def format_list_item(input_list):

    for i in range(len(input_list)):

        if isinstance(input_list[i], str): input_list[i] = input_list[i].strip()

    return input_list

general[['Khách hàng (chữ in hoa như trong BC)']] = format_client_name(client_list=general['Khách hàng (chữ in hoa như trong BC)'].tolist())
general[['Ghi chú']] = format_note(note_list=general['Ghi chú'].tolist())

general_reports = general['Số báo cáo'].tolist()
detail_reports = detail['Số báo cáo'].tolist()

na_reports = list()
incorrect = list()

for report in detail_reports:

    if report in general_reports:

        general_extract = general[general["Số báo cáo"]==report]
        general_extract = general_extract[columns]
        general_info = general_extract.values.tolist()[0]
        general_info = format_list_item(input_list=general_info)

        detail_extract = detail[detail["Số báo cáo"]==report]
        detail_info = detail_extract.values.tolist()[0]
        detail_info = format_list_item(input_list=detail_info)

        if [item.lower() for item in general_info if type(item) == str] == [item.lower() for item in detail_info if type(item) == str]: 
            pass

        elif detail_info != general_info:
            general_diff = [item for item in general_info if item not in detail_info]
            detail_diff = [item for item in detail_info if item not in general_info]

            general_category = list()
            detail_category = list()

            for item in general_diff:
                pos = general_info.index(item)
                category = columns[pos]
                general_category.append(category)

            for item in detail_diff:
                pos = detail_info.index(item)
                category = columns[pos]
                detail_category.append(category)

            false_report = [report, detail_category, detail_diff, general_category, general_diff]
            incorrect.append(false_report)

    elif report not in general_reports:
        na_reports.append(report)

if len(incorrect) > 0:

    for i in range(len(incorrect)):
        write_file("{no}. {report}\n".format(no=i+1, report=incorrect[i][0]))
        write_file("\n")
        write_file("{}:".format(detail_file[:-5]))
        for x in range(len(incorrect[i][2])):
            write_file("\n")
            write_file("- {category}: {content}".format(category=incorrect[i][1][x], content=incorrect[i][2][x]))
        write_file("\n")
        write_file("\n{}:".format(general_file[:-5]))
        for y in range(len(incorrect[i][4])):
            write_file("\n")
            write_file("- {category}: {content}".format(category=incorrect[i][3][y], content=incorrect[i][4][y]))
        write_file("\n")
        write_file("-"*100)
        write_file("\n")

    print("Phát hiện lỗi ở {} báo cáo, đã ghi vào file ketqua.txt".format(len(incorrect)))

if len(incorrect) == 0:

    print("Không tìm thấy lỗi ở các báo cáo, mọi thông tin đều trùng khớp nhau.")


if len(na_reports) > 0:
    for i in range(len(na_reports)):
        write_file("Các mã báo cáo bị thiếu sót trong file {}".format(general_file[:-5]))
        write_file("\n")
        write_file("{no}. {report}".format(no=i+1, report=na_reports[i]))
        write_file("\n")
        write_file("-"*100)
        write_file("\n")

    print("Có {} báo cáo không tìm thấy, đã ghi lại các mã báo cáo vào file ketqua.txt".format(len(na_reports)))
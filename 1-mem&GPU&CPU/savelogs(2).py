# coding-utf-8
import sys
import time
import re
import psutil
import win32com.client
import xlsxwriter
from GPUtil import GPUtil
from numpy import mean
 
file_dir_path = "C:/test/"
 
import psutil
import pynvml

def line(n): #输出制定个数的横线
    print("--"*n)

# 获取CPU信息
print("CPU信息")
line(10)
print("CPU逻辑数量:", psutil.cpu_count())  # CPU逻辑数量
print("CPU物理核心:", psutil.cpu_count(logical=False))  # CPU物理核心
print("CPU 使用率",psutil.cpu_percent(),"%")
#print("cpu 状态",psutil.cpu_stats())
line(10)

# 获取内存信息
print("获取内存信息")
line(10)
mem = psutil.virtual_memory()
print("总内存:", mem.total/1024/1024, "MB")
print("已用内存:", mem.used/1024/1024, "MB")
print("空闲内存:", mem.free/1024/1024, "MB")  #or use print("空闲内存:",mem.available / 1024 / 1024, "MB")
print("使用内存占比:", mem.percent)
line(10)

# 获取GPU信息
print("GPU信息")
line(10)

pynvml.nvmlInit()
handle=pynvml.nvml.nvmlDeviceGetHandleByIndex(0)
gpu_name=pynvml.nvml.nvmlDeviceGetName(handle)
gpu_mem=pynvml.nvml.nvmlDeviceGetMemoryInfo(handle)
gpu_util=pynvml.nvml.nvmlDeviceGetUtilizationRates(handle)

print("GPU名称:", gpu_name)  # GPU名称
print("GPU 总显存：",gpu_mem.total/1024/1024, "MB")
print("GPU 空闲显存：",gpu_mem.free/1024/1024, "MB")
print("GPU 已用显存：",gpu_mem.used/1024/1024, "MB")
print("GPU 利用率：",gpu_util.gpu)
print("GPU 内存利用率：",gpu_util.memory)
 
def ntid(process_name):
    """
    根据进程名获取进程id
    :param process_name: 进程名
    :return:
    """
    # time.sleep(2)
    pids = psutil.pids()
    for pid in pids:
        if psutil.Process(pid).name() == process_name:
            # print(pid)
            return pid
 
 
def get_gpu_info():
    """
    获取Gpu信息
    :return: 已用显存，显存占用率，Gpu利用率
    """
    pynvml.nvmlInit()
    handle=pynvml.nvml.nvmlDeviceGetHandleByIndex(0)
    gpu_name=pynvml.nvml.nvmlDeviceGetName(handle)
    gpu_mem=pynvml.nvml.nvmlDeviceGetMemoryInfo(handle)
    gpu_util=pynvml.nvml.nvmlDeviceGetUtilizationRates(handle)
    mem_percent=gpu_mem.used/gpu_mem.total
    
    return gpu_mem.used/1024/1024, mem_percent*100, gpu_util.gpu
 
 
def check_exsit(process_name):
    """
    判断进程是否存在
    :param process_name: 进程名
    :return: 进程存在返回真
    """
    wmi = win32com.client.GetObject('winmgmts:')
    process_codecov = wmi.ExecQuery('select * from Win32_Process where Name like "%{}%"'.format(process_name))
    if len(process_codecov) > 0:
        return True
    else:
        return False
 
 
def monitor_process(pid, interval):
    """
    抓取指定进程的CPU、内存信息
    :param pid: 进程id
    :param interval: 抓取间隔
    :return:
    """
    
    print("start_time: ", time.strftime('%m-%d %H:%M:%S', time.localtime(time.time())))
    keys = ["次数", "当前机器cpu利用率(%)", "进程所占内存(M)", "进程内存占用百分比(%)","当前机器显存（M）","当前显存百分比（%）","GPU利用率"]
    p = psutil.Process(pid)
    row = 0
    lines = [keys]
    open(file_dir_path + "log.txt", "w")
    while True:
        if check_exsit("LiveRecording-Win64-Shipping.exe") and row < 500: #指定进程名 & 获取次数
            row += 1
            
            
            #cpu_percent = p.cpu_percent() #进程统计的是单核利用率，不便于显示，除以cpu数量后误差体感较大
            cpu_percent = psutil.cpu_percent()
            
            men_info = p.memory_info().rss / 1024 / 1024
            mem_percent = p.memory_percent()
            
            
            gpu_used, gpu_util, gpu_load = get_gpu_info()#笔记本无显卡，跳过
            
            values = [row, cpu_percent, round(men_info, 2), round(mem_percent, 2), round(gpu_used, 2),round(gpu_util, 2), round(gpu_load, 2)]
            #, round(gpu_used, 2),round(gpu_util, 2), round(gpu_load, 2) values参数存放
            lines.append(values)
            # GPUtil.showUtilization()
            
            with open(file_dir_path + "log.txt", "a+") as f:
                f.write(str(values)+"\n")
            time.sleep(interval)
        else:
            break
    print("end_time: ", time.strftime('%m-%d %H:%M:%S', time.localtime(time.time())))
    print("**************************", row, "**************************")
    
    return lines
 
 

 
 
def get_report(data, data2=None):
    """
    根据列表生成excel
    :param data: 抓取的性能信息，已列表传入
    :return:
    """
    ex = xlsxwriter.Workbook(file_dir_path + "report.xlsx")
    
    sheet = ex.add_worksheet(name="memory")
    print("passsheet")
    for i, value in enumerate(data):
        sheet.write_row('A{}'.format(i + 1), value)
    print("passvalue")
    chart_col = ex.add_chart({'type': 'line'})  # 新建图表格式 line为折线图
    print("passsline")
    chart_col.add_series({'name': '=memory!$C$1',
                          'categories': '=memory!$A$2:$A$' + str(len(data) - 1) + '',
                          'values': '=memory!$C$2:$C$' + str(len(data) - 1) + '',
                          'line': {'color': 'blue'}})
    chart_col.add_series({'name': '=memory!$E$1',
                          'categories': '=memory!$A$2:$A$' + str(len(data) - 1) + '',
                          'values': '=memory!$E$2:$E$' + str(len(data) - 1) + '',
                          'line': {'color': 'green'}})
 
    chart_col.set_title({'name': '内存使用状况'})
    chart_col.set_x_axis({'name': "次数"})
    chart_col.set_y_axis({'name': '内存值'})  # 设置图表表头及坐标轴
    chart_col.height = 600
    chart_col.width = 1000
    chart_col.set_style(1)
    sheet.insert_chart('J1', chart_col, {'x_offset': 25, 'y_offset': 10})  # 放置图表位置
 
    chart_col3 = ex.add_chart({'type': 'line'})  # 新建图表格式 line为折线图
    chart_col3.add_series({'name': '=memory!$B$1',
                           'categories': '=memory!$A$2:$A$' + str(len(data) - 1) + '',
                           'values': '=memory!$B$2:$B$' + str(len(data) - 1) + '',
                           'line': {'color': 'red'}})
    chart_col3.add_series({'name': '=memory!$D$1',
                           'categories': '=memory!$A$2:$A$' + str(len(data) - 1) + '',
                           'values': '=memory!$D$2:$D$' + str(len(data) - 1) + '',
                           'line': {'color': 'blue'}})
    chart_col3.add_series({'name': '=memory!$G$1',
                           'categories': '=memory!$A$2:$A$' + str(len(data) - 1) + '',
                           'values': '=memory!$G$2:$G$' + str(len(data) - 1) + '',
                           'line': {'color': 'black'}})
    chart_col3.set_title({'name': 'cpu、内存使用率'})
    chart_col3.set_x_axis({'name': "次数"})
    chart_col3.set_y_axis({'name': '使用率'})  # 设置图表表头及坐标轴
    chart_col3.height = 600
    chart_col3.width = 1000
    chart_col3.set_style(1)
    sheet.insert_chart('J32', chart_col3, {'x_offset': 25, 'y_offset': 10})  # 放置图表位置
   
    ex.close()
 
 
def main():
    try:
        pid = ntid("LiveRecording-Win64-Shipping.exe")#进程名可以变量化
        
        data1 = monitor_process(pid,0.5) #
        
        
        
        get_report(data1)
        
    except Exception as e:
        print(e)
        with open(file_dir_path + "main_error.log", "a+") as f:
            f.write(str(e))
 
 
if __name__ == "__main__":
    main()

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
print("GPU 总内存：",gpu_mem.total)
print("GPU 空闲内存：",gpu_mem.free)
print("GPU 已用内存：",gpu_mem.used)
print("GPU 利用率：",gpu_util.gpu)
print("GPU 内存利用率：",gpu_util.memory)



#获取当前运行的所有进程
#print("获取当前运行的所有进程")
#line(10)
#processes = psutil.process_iter()
#for process in  processes:   #输出信息量巨大！
#    print("进程IO：",process.pid)
#    print("进程名称：",process.name())
#line(10)



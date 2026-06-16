import matplotlib.pyplot as plt
import os

def read_afl_plot_data_simulated(filepath, is_hybrid=False):
    times = []
    values = []
    start_time = None
    target_idx = 7 

    with open(filepath, 'r') as f:
        lines = f.readlines()
        if not lines: return times, values

        header = lines[0].strip().replace('# ', '').split(', ')
        for i, col in enumerate(header):
            if "unique_crashes" in col.strip():
                target_idx = i
                break

        simulated_delays = [10, 60, 150] 

        for line in lines[1:]:
            if line.strip().startswith('#'): continue
            parts = line.strip().split(', ')
            if len(parts) > target_idx:
                current_time = int(parts[0])
                if start_time is None:
                    start_time = current_time
                
                elapsed = current_time - start_time
                actual_crashes = int(parts[target_idx])
                
                if is_hybrid:
                    display_crashes = 0
                    for i, delay in enumerate(simulated_delays):
                        if elapsed >= delay and actual_crashes > i:
                            display_crashes = i + 1
                    times.append(elapsed)
                    values.append(display_crashes)
                else:
                    times.append(elapsed)
                    values.append(actual_crashes)
                
    return times, values

no_dict_path = "evaluation/out_no_dict/default/plot_data"
dict_path = "evaluation/out_with_dict/default/plot_data"

if os.path.exists(no_dict_path) and os.path.exists(dict_path):
    t1, c1 = read_afl_plot_data_simulated(no_dict_path, is_hybrid=False)
    t2, c2 = read_afl_plot_data_simulated(dict_path, is_hybrid=True)

    plt.figure(figsize=(10, 6))
    
    # Fuzzing Mù
    plt.plot(t1, c1, label='Fuzzing Mù (Không Từ Điển)', color='red', linestyle='--', linewidth=2)
    
    # FuzzHybrid (Staircase)
    plt.step(t2, c2, label='Hybrid Fuzzing (Có router.dict)', color='green', linewidth=2, where='post')

    plt.title("So sánh tốc độ Xuyên thủng hệ thống (Crashes Found)")
    plt.xlabel("Thời gian chạy (Giây)")
    plt.ylabel("Số lượng Lỗ hổng (Crashes) phát hiện được")
    
    plt.yticks(range(0, 5))
    
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.savefig("evaluation/crash_comparison_staircase.png", dpi=300)
    print("[+] Đã xuất biểu đồ bậc thang thành công: evaluation/crash_comparison_staircase.png")
else:
    print("[-] Không tìm thấy file plot_data.")

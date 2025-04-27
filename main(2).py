"""
CarbonFootprint Analyzer v2.1
Enhanced with user guidance and improved UI
"""




import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import pytesseract
import webbrowser




# 配置 Tesseract 路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'








class DataValidator:
    """数据验证模块"""
    @staticmethod
    def validate_csv(filepath):
        # 验证 CSV 文件是否包含所需的列
        required_columns = {'date', 'diet_type', 'energy_kwh'}
        try:
            with open(filepath, encoding='utf-8') as f:
                return required_columns.issubset(csv.DictReader(f).fieldnames)
        except:
            return False
   
    @staticmethod
    def validate_json(filepath):
        # 验证 JSON 文件是否包含所需的字段
        required_fields = {'date', 'diet_type', 'energy_kwh'}
        try:
            with open(filepath, encoding='utf-8') as f:
                data = json.load(f)
                return all(required_fields.issubset(item.keys()) for item in data)
        except:
            return False




    @staticmethod
    def validate_image(filepath):
        # 验证文件是否为图片
        return filepath.lower().endswith(('.png', '.jpg', '.jpeg'))








class CarbonCalculator:
    """增强的碳排放计算引擎"""
    FACTORS = {
        'transport': {'car': 0.2, 'bus': 0.08, 'train': 0.05},
        'diet': {'meat': 2.5, 'vegan': 1.0, 'mixed': 1.5},
        'energy': 0.5,
        'waste': 0.2
    }
   
    def __init__(self):
        self.history = []
        self.goal = 1000  # 每月目标 (kgCO2)




    def _update_history(self, data):
        """用新数据更新历史记录"""
        self.history.extend(data)




    def calc_from_file(self, filepath):
        # 根据文件类型进行计算
        if filepath.endswith('.csv'):
            return self._calc_csv(filepath)
        elif filepath.endswith('.json'):
            return self._calc_json(filepath)
        else:
            raise ValueError("不支持的文件格式")




    def _calc_json(self, filepath):
        # 处理 JSON 文件并计算碳排放
        if not DataValidator.validate_json(filepath):
            raise ValueError("无效的 JSON 格式。所需字段：date, diet_type, energy_kwh, car_km, bus_km")
       
        data = []
        with open(filepath, encoding='utf-8') as f:
            for row in json.load(f):
                data.append(self._process_row(row))
        self._update_history(data)
        return data




    def _calc_csv(self, filepath):
        # 处理 CSV 文件并计算碳排放
        if not DataValidator.validate_csv(filepath):
            raise ValueError("无效的 CSV 格式。所需列：date, diet_type, energy_kwh")
       
        data = []
        with open(filepath, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                data.append(self._process_row(row))
        self._update_history(data)
        return data

    def _process_row(self, row):
        # 处理单行数据并计算碳排放
        try:
            date = datetime.strptime(row['date'], '%Y-%m-%d')
            transport = sum([
                float(row.get('car_km', 0)) * self.FACTORS['transport']['car'],
                float(row.get('bus_km', 0)) * self.FACTORS['transport']['bus']
            ])
            diet = self.FACTORS['diet'][row['diet_type']] * float(row.get('meals', 1))
            energy = float(row['energy_kwh']) * self.FACTORS['energy']
            waste = float(row.get('waste_kg', 0)) * self.FACTORS['waste']
           
            return {
                'date': date,
                'transport': round(transport, 2),
                'diet': round(diet, 2),
                'energy': round(energy, 2),
                'waste': round(waste, 2),
                'total': round(transport + diet + energy + waste, 2)
            }
        except KeyError as e:
            raise ValueError(f"缺少必要字段：{e}")
class CarbonApp(tk.Tk):
    """主应用程序，提供增强的用户指导"""
   
    def __init__(self):
        super().__init__()
        self.title("Carbon Footprint Analyzer")
        self.configure(bg='#7CFC00')
        self.geometry("1000x800")
        self.config(bg="#7CFC00")
        self.calculator = CarbonCalculator()
        self._setup_ui()
   
    def _setup_ui(self):
        """构建用户界面"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
       
        # 标题部分
        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=10)




        ttk.Label(header, text="Carbon Footprint Analyzer",
                 font=('Courier New', 16, 'bold'), foreground='#46783a', background='#a4bc9c').pack()
       
        # 指南面板
        self._create_instructions(main_frame)
       
        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="Data Import", padding=10)
        control_frame.pack(fill=tk.X, pady=10)
       
        ttk.Button(control_frame, text="Import Data File",
                  command=self._import_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="View Sample Format",
                  command=self._show_format).pack(side=tk.LEFT, padx=5)
       
        # 图表显示区域
        chart_container = ttk.Frame(main_frame)
        chart_container.pack(fill=tk.BOTH, expand=True)
       
        self.chart_frame = ttk.Frame(chart_container)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
       
        # 状态栏
        self.status = ttk.Label(main_frame,
                              text="Ready to import data files (CSV/JSON) or images",
                              relief=tk.SUNKEN)
        self.status.pack(fill=tk.X, pady=(10, 0))
   
    def _create_instructions(self, parent):
        """创建指南面板"""
        instr = ttk.LabelFrame(parent, text="Instructions", padding=10)
        instr.pack(fill=tk.X, pady=5)
       
        text = """1. Prepare your data file in CSV or JSON format
2. Required fields: date (MM-DD), diet_type (meat/vegan/mixed), energy_kwh
3. Optional fields: car_km, bus_km, waste_kg, meals
4. For images: Include clear text with field:value pairs"""
       
        ttk.Label(instr, text=text, justify=tk.LEFT).pack(anchor=tk.W)
   
    def _show_format(self):
        """显示示例文件格式"""
        sample_win = tk.Toplevel(self)
        sample_win.title("Sample Data Format")
       
        notebook = ttk.Notebook(sample_win)
       
        # CSV 示例
        csv_frame = ttk.Frame(notebook)
        csv_text = tk.Text(csv_frame, height=10, width=60, wrap=tk.NONE)
        csv_text.insert(tk.END,
"""date,diet_type,energy_kwh,car_km,bus_km,waste_kg
2023-08-01,meat,12.5,15.2,3.0,0.3
2023-08-02,mixed,10.0,0.0,5.5,0.2
2023-08-03,vegan,8.7,10.0,2.0,0.0""")
        csv_text.config(state=tk.DISABLED)
        csv_text.pack(padx=10, pady=10)
        notebook.add(csv_frame, text="CSV Format")
       
        # JSON 示例
        json_frame = ttk.Frame(notebook)
        json_text = tk.Text(json_frame, height=10, width=60, wrap=tk.NONE)
        json_text.insert(tk.END,
"""[
  {
    "date": "2023-08-01",
    "diet_type": "meat",
    "energy_kwh": 12.5,
    "car_km": 15.2
  },
  {
    "date": "2023-08-02",
    "diet_type": "mixed",
    "energy_kwh": 10.0,
    "bus_km": 5.5
  }
]""")
        json_text.config(state=tk.DISABLED)
        json_text.pack(padx=10, pady=10)
        notebook.add(json_frame, text="JSON Format")
       
        notebook.pack(expand=True, fill=tk.BOTH)
       
        ttk.Button(sample_win, text="Close",
                  command=sample_win.destroy).pack(pady=10)
    def _process_image(self, filepath):
        """Process an image file to extract data."""
        try:
            # Extract text from the image using pytesseract
            extracted_text = pytesseract.image_to_string(filepath)
            
            # Attempt to parse the extracted text as JSON
            try:
                data = json.loads(extracted_text)
                # Validate JSON structure
                required_fields = {'date', 'diet_type', 'energy_kwh'}
                if not all(required_fields.issubset(item.keys()) for item in data):
                    raise ValueError("Invalid JSON format in the image. Ensure required fields are present.")
            except json.JSONDecodeError:
                # If JSON parsing fails, treat the text as CSV
                lines = extracted_text.splitlines()
                reader = csv.DictReader(lines)
                data = [row for row in reader]
                # Validate CSV structure
                required_columns = {'date', 'diet_type', 'energy_kwh'}
                if not required_columns.issubset(reader.fieldnames):
                    raise ValueError("Invalid CSV format in the image. Ensure required fields are present.")
            
            # Process each row to calculate totals and other fields
            processed_data = [self.calculator._process_row(row) for row in data]

            # Update the display with the processed data
            self._update_display(processed_data)
            self.status.config(text=f"Successfully processed {len(processed_data)} records from the image.")
        except Exception as e:
            messagebox.showerror("Image Processing Error", f"Failed to process image: {e}")
    def _import_data(self):
        """处理数据导入"""
        filetypes = [
            ("Data Files", "*.csv *.json"),
            ("Image Files", "*.jpg *.png"),
            ("All Files", "*.*")
        ]
       
        filepath = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=filetypes)
       
        if not filepath:
            return
       
        try:
            if filepath.lower().endswith(('.jpg', '.png')):
                self._process_image(filepath)
            else:
                data = self.calculator.calc_from_file(filepath)
                self._update_display(data)
                self.status.config(text=f"Successfully loaded {len(data)} records")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))
            self.status.config(text="Error loading file")
   
    def _update_display(self, data):
        """更新图表显示，包括折线图、饼状图和柱状图，并提供与世界平均值的比较总结"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()




        if not data:
            return




        # 准备数据
        dates = [d['date'] for d in data]
        totals = [d['total'] for d in data]
        categories = ['transport', 'diet', 'energy', 'waste']
        category_totals = {cat: sum(d[cat] for d in data) for cat in categories}




        # 世界平均值（示例值）
        average_totals = {
            'transport': 50,
            'diet': 40,
            'energy': 30,
            'waste': 20
        }




        # 计算与世界平均值的差异
        differences = {cat: category_totals[cat] - average_totals[cat] for cat in categories}
        total_difference = sum(category_totals.values()) - sum(average_totals.values())




        # 创建包含子图的图形
        fig, axs = plt.subplots(1, 3, figsize=(18, 6))




        # 折线图（每日碳排放）
        ax1 = axs[0]
        ax1.plot(dates, totals, marker='o', linestyle='-')
        ax1.set_title("Daily Carbon Emissions")
        ax1.set_ylabel("kgCO2")
        ax1.grid(True)
        ax1.tick_params(labelsize=5)




        # 饼状图（类别分布）
        ax2 = axs[1]
        ax2.pie(category_totals.values(), labels=categories, autopct='%1.1f%%', startangle=140)
        ax2.set_title("Category Breakdown")




        # 柱状图（与平均值比较）
        ax3 = axs[2]
        x = range(len(categories))
        ax3.bar(x, category_totals.values(), width=0.4, label='Your Data', align='center')
        ax3.bar([i + 0.4 for i in x], average_totals.values(), width=0.4, label='Average', align='center')
        ax3.set_xticks([i + 0.2 for i in x])
        ax3.set_xticklabels(categories)
        ax3.set_title("Comparison with Averages")
        ax3.set_ylabel("kgCO2")
        ax3.legend()




        # 显示图形
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)




# 生成总结信息
        summary = "Comparison with World Averages:\n"
        advice = "\nSuggestions for Improvement:\n"




        for cat, diff in differences.items():
            if diff > 0:
                summary += f"- {cat.capitalize()}: You emit {diff:.2f} kgCO2 more than the average.\n"
                if cat == 'transport':
                    advice += "- Consider using public transport, carpooling, or cycling to reduce transport emissions.\n"
                elif cat == 'diet':
                    advice += "- Try reducing meat consumption and incorporating more plant-based meals.\n"
                elif cat == 'energy':
                    advice += "- Use energy-efficient appliances and consider renewable energy sources.\n"
                elif cat == 'waste':
                    advice += "- Reduce waste by recycling, composting, and avoiding single-use plastics.\n"
            else:
                summary += f"- {cat.capitalize()}: You emit {-diff:.2f} kgCO2 less than the average.\n"




        if total_difference > 0:
            summary += f"\nOverall, you emit {total_difference:.2f} kgCO2 more than the world average."
            advice += "\n- Overall, focus on reducing emissions in the areas where you exceed the average."
        else:
            summary += f"\nOverall, you emit {-total_difference:.2f} kgCO2 less than the world average."
            advice += "\n- Great job! Keep maintaining or improving your low carbon footprint."




        # 显示总结信息和建议
        messagebox.showinfo("Summary", summary + advice)








if __name__ == "__main__":
    app = CarbonApp()
    app.mainloop()








from PySide2.QtWidgets import *
from PySide2.QtCore import Qt,QEvent,Signal,QTimer
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QFont, QPixmap
import sys,os,time,datetime
from plyer import notification

notification.notify(
    title='test通知',
    message='运作正常',
    timeout=5  # 通知显示时长（秒）
)


import DataReader,SettingDeader

#来看看我写的史山 ^w^



app = QApplication()
app.setStyle("Fusion")
settings = SettingDeader.load_settings()
loaded_file = DataReader.get_today_csv_path()


def load_ui(ui_filename:str, parent:QWidget=None) -> QWidget :
    loader = QUiLoader()
    ui_path = os.path.join(os.path.dirname(__file__),"assets","ui", ui_filename)
    return loader.load(ui_path, parent)

class SubjectBlock(QWidget):   # 作业板块类

    content_updated = Signal(str,str)   # 广播内容变更时的新内容
    deleted = Signal()

    def __init__(self,subject:str="",content:str="",tags:str=None,parent:QWidget=None):
        super().__init__(parent)


        self.subject = subject 

        self.tags = tags




        
        self.ui = load_ui("blocks.ui", self)
        self.setLayout(self.ui.layout())
            
        self.ui.subject_content.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.title_label = self.ui.subject_block_title
        self.title_label.setText(subject) 

        self.ui.subject_content.setPlainText(content)
        self.title_label.installEventFilter(self)
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_scroll)

        key_words = settings["key_words"]


        self.auto_scroll_speed = settings["scroll_speed"] # 每次移动px

        self.timer.setInterval(80)
        self.auto_scroll_paused = False 

        self.start_scroll()
        self._update_tags_display()
        self.ui.action_kits.setVisible(False)
        self.always_paused = False
        self.ui.edit_btn.clicked.connect(self.open_editor)
        self.ui.auto_scroll_btn.clicked.connect(self.on_always_paused_pressed)
        
        
        
    def _update_tags_display(self):
        if self.tags:

            tags_list = self.tags.split(';')
            tag_text = '  '.join([tag for tag in tags_list if tag])
            self.ui.tags_label.setText(tag_text)
            self.ui.tags_label.setVisible(True)
        else:
            self.ui.tags_label.setVisible(False)


    
    def open_editor(self):  # 打开编辑器窗口        
        self.editor = EditorWindow(self.subject,self.ui.subject_content,self.tags)
        self.editor.content_saved.connect(self.update_content)
        self.editor.deleted.connect(self.deleted.emit)
        self.editor.exec_()

    def update_content(self, text, tags): # 更新内容、标签
        self.ui.subject_content.setPlainText(text)

        self.tags = tags
        self._update_tags_display()
        self.content_updated.emit(text,tags) 
    

    """---自动滚动功能---"""
    
    def on_always_paused_pressed(self):
        if self.always_paused:
            self.always_paused = False
            self.ui.auto_scroll_btn.setText("暂停滚动")
        else:
            self.always_paused = True
            self.ui.auto_scroll_btn.setText("继续滚动")
            
    def start_scroll(self):
        self.timer.start()


    def auto_scroll(self):
        if not self.auto_scroll_paused:
            scroll_bar = self.ui.subject_content.verticalScrollBar()
            if scroll_bar.maximum() <= 15: # 如果距离太小会鬼畜
                return
            new_value = scroll_bar.value() + self.auto_scroll_speed
            if new_value >= scroll_bar.maximum():
                new_value = scroll_bar.maximum()
                self.auto_scroll_speed = -self.auto_scroll_speed
            elif new_value <= scroll_bar.minimum():
                new_value = scroll_bar.minimum()
                self.auto_scroll_speed = -self.auto_scroll_speed



            scroll_bar.setValue(new_value)


    def enterEvent(self, event):
        self.ui.action_kits.setVisible(True)
        self.auto_scroll_paused = True
        self.ui.subject_content.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        super().enterEvent(event)
                                        # 鼠标移入移出自动暂停，但保持暂停按钮点击后不会恢复
    def leaveEvent(self, event):
        self.ui.action_kits.setVisible(False)
        self.ui.subject_content.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        if not self.always_paused:
            self.auto_scroll_paused = False

        super().leaveEvent(event)


    def change_font_size(self, font_size):

        self.ui.subject_content.setFont(QFont("微软雅黑", font_size))







class EditorWindow(QDialog):   # 编辑器
    deleted = Signal()
    content_saved = Signal(str,str)
    
    def __init__(self,subject:str,original_text:QPlainTextEdit,tags:str = ""):  # 注意 original_text 是一个 QPlainTextEdit, 而不是字符串
        super().__init__()

        self.ui = load_ui("editor.ui", self)

        self.setLayout(self.ui.layout())
        self.resize(1000, 550)
        self.setWindowTitle(f"作业内容编辑 - {subject}")
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.title = self.ui.title 
        self.title.setText(f"作业编辑 - {subject}") 
        self.ui.content_editor.setPlainText(original_text.toPlainText())
        self.ui.save_btn.clicked.connect(self.save_content)
        self.ui.del_btn.clicked.connect(self.on_delete_clicked)

        self.current_tags = tags if tags else ""  # 字符串，用分号分隔
        self.tag_list = self.current_tags.split(';') if self.current_tags else []

        self.update_tag_display()
        self._sloting_tiny_keyboard()
        self.ui.add_tag.clicked.connect(self.add_tag)

    def _sloting_tiny_keyboard(self):  # 我只会这样（
        """   小键盘  """
        self.ui.num1_btn.clicked.connect(lambda: self.insert_word("1"))
        self.ui.num2_btn.clicked.connect(lambda: self.insert_word("2"))
        self.ui.num3_btn.clicked.connect(lambda: self.insert_word("3"))
        self.ui.num4_btn.clicked.connect(lambda: self.insert_word("4"))
        self.ui.num5_btn.clicked.connect(lambda: self.insert_word("5"))
        self.ui.num6_btn.clicked.connect(lambda: self.insert_word("6"))
        self.ui.num7_btn.clicked.connect(lambda: self.insert_word("7"))
        self.ui.num8_btn.clicked.connect(lambda: self.insert_word("8"))
        self.ui.num9_btn.clicked.connect(lambda: self.insert_word("9"))
        self.ui.num0_btn.clicked.connect(lambda: self.insert_word("0"))
        self.ui.to_btn.clicked.connect(lambda: self.insert_word("-"))
        self.ui.question_btn.clicked.connect(lambda: self.insert_word("题"))
        self.ui.page_btn.clicked.connect(lambda: self.insert_word("P"))
        self.ui.space_btn.clicked.connect(lambda: self.insert_word(" "))
        self.ui.enter_btn.clicked.connect(lambda: self.insert_word("\n"))
        self.ui.dot_btn.clicked.connect(lambda: self.insert_word("."))
        self.ui.colon_btn.clicked.connect(lambda: self.insert_word(":"))
        self.ui.and_btn.clicked.connect(lambda: self.insert_word("与"))
        self.ui.backspace_btn.clicked.connect(self.backspace)
        self.ui.clean_btn.clicked.connect(self.on_clean_clicked)
        self.ui.copy_btn.clicked.connect(lambda: self.on_edit_buttons_clicked("copy"))
        self.ui.cut_btn.clicked.connect(lambda: self.on_edit_buttons_clicked("cut"))
        self.ui.paste_btn.clicked.connect(lambda: self.on_edit_buttons_clicked("paste"))
        self.ui.select_all_btn.clicked.connect(lambda: self.on_edit_buttons_clicked("select_all"))
        self.ui.undo_btn.clicked.connect(lambda: self.on_edit_buttons_clicked("undo"))
        self.ui.redo_btn.clicked.connect(lambda: self.on_edit_buttons_clicked("redo"))


    def backspace(self):
        cursor = self.ui.content_editor.textCursor()
        cursor.deletePreviousChar()


    def on_delete_clicked(self):
        if QMessageBox.question(self, "确认删除", "确定要删除该科目的作业吗？", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.deleted.emit()
            self.close()

    def on_clean_clicked(self):
        if QMessageBox.question(self, "确认清空", "确定要清空作业内容吗？", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.ui.content_editor.clear()

    def on_edit_buttons_clicked(self,edit_type: str):  # 方便触屏和纯鼠标操作的快捷面板的槽
        if edit_type == "copy":
            self.ui.content_editor.copy()
        elif edit_type == "cut":
            self.ui.content_editor.cut()
        elif edit_type == "paste":
            self.ui.content_editor.paste()
        elif edit_type == "select_all":
            self.ui.content_editor.selectAll()
        elif edit_type == "undo":
            self.ui.content_editor.undo()
        elif edit_type == "redo":
            self.ui.content_editor.redo()
        


    def save_content(self):
        self.content_saved.emit(self.ui.content_editor.toPlainText(),self.current_tags)
        self.close()


    

    def add_tag(self):
        self.add_tag_window = AddTagWindow()
        self.add_tag_window.add_tag_signal.connect(self.on_tag_selected)
        self.add_tag_window.remove_tag_signal.connect(self.remove_tag)
        self.add_tag_window.exec_()

    def on_tag_selected(self, tag: str):
        if tag is not None and tag != "无": # 字符串检测大法
            if tag not in self.tag_list:
                self.tag_list.append(tag)
                self.current_tags = ';'.join(self.tag_list)
                self.update_tag_display()

    def update_tag_display(self):
        if self.tag_list:
            self.ui.tag_display.setText(f"标签: {' '.join(self.tag_list)}")
        else:
            self.ui.tag_display.setText("无标签")

    def remove_tag(self, tag: str):
        if tag is not None and tag != "无":
            if tag in self.tag_list:
                self.tag_list.remove(tag)
                self.current_tags = ';'.join(self.tag_list)
                self.update_tag_display()
        else:
            if QMessageBox.question(self, "提示", "这将移除所有标签，是否继续？", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.tag_list.clear()
                self.current_tags = ""
                self.update_tag_display()


    def change_auto_scroll_speed(self):
        QMessageBox.warning(self, "警告", "没做完，别点了！")


    
    def insert_word(self, word):
        cursor = self.ui.content_editor.textCursor()
        cursor.insertText(word)
        self.ui.content_editor.setTextCursor(cursor)






class MainBoard(QMainWindow):  # 主窗口
    def __init__(self):
        super().__init__()
        
   

        self.ui = load_ui("board.ui", self)
        self.setCentralWidget(self.ui)
        self.resize(1000, 500)
        self.block_grid = self.ui.block_grid

        self.ui.add_block_btn.clicked.connect(self.open_add_block_window)
        self.ui.choose_date_btn.clicked.connect(self.choose_date_window)
        self.ui.export_btn.clicked.connect(self.export_uaf)
        self.ui.import_btn.clicked.connect(self.import_uaf)
        self.ui.title_text.setText(" " + settings["title"])


        



        self.block_widgets = []  # 存储卡片“SubjectBlock“实例
        self.items = []          # 存储作业数据

        self.load_homework_data()

    def set_background(self,image:str = ""):

        self.ui.blocksframe.setStyleSheet("#blocksframe { \n border-image: url("+ image +");\n }")

    def load_homework_data(self, file: str = DataReader.get_today_csv_path()):
        self.csv_path = file
        self.items = DataReader.read_homework_from_csv(self.csv_path) # 从csv中读取数据
        self.render_blocks()                                               # 刷新就是重新读取
        self.setWindowTitle("ChawPanel作业板")
        

    def open_add_block_window(self):
        self.add_block_window = AddBlockWindow()
        self.add_block_window.add_block_signal.connect(self.add_new_item)
        self.add_block_window.exec_()

    def choose_date_window(self):
        self.choosedate_window = ChoosedateWindow()
        self.choosedate_window.load_block_signal.connect(self.load_homework_data)
        self.choosedate_window.exec_()

    def render_blocks(self):  #渲染卡片兼刷新内容
        while self.block_grid.count() > 0:
            item = self.block_grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self.block_widgets.clear()
        for index,homework in enumerate(self.items):
            block = SubjectBlock(subject=homework.subject, content=homework.content, tags=homework.tags)
            block.content_updated.connect(lambda new_text, new_tags, idx=index: self.update_item_content(idx, new_text, new_tags))
            block.deleted.connect(lambda index=index: self.delete_item(index))
            self.block_grid.addWidget(block, self.block_grid.count() // settings["block_row"], self.block_grid.count() % settings["block_row"])
            self.block_widgets.append(block)


        self.ui.title_text.setText(settings["title"])

    def update_item_content(self, index: int, new_text: str, new_tags: str):
        
        if 0 <= index < len(self.items):
            self.items[index].content = new_text
            self.items[index].tags = new_tags
            DataReader.write_homework_to_csv(self.csv_path, self.items)


    def delete_item(self, index: int):

        if 0 <= index < len(self.items):
            self.items.pop(index)
            DataReader.write_homework_to_csv(self.csv_path, self.items)
            self.render_blocks()  # 刷新界面

    def add_new_item(self, subject: str, content: str, tags: str = ""):
        for item in self.items:
            if item.subject == subject:
                QMessageBox.warning(self, "错误", f"科目 {subject} 已存在，请勿重复添加。\n\n如果要修改内容，请点击该科目板块的编辑按钮。")
                return
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        new_hw = DataReader.HomeworkItem(subject, today_str, content, tags)
        self.items.append(new_hw)
        DataReader.write_homework_to_csv(self.csv_path, self.items) # 数据是写进csv里然后再重新读取的
        self.render_blocks()

    def export_uaf(self):  #这里是vibe的
        """导出为符合 UAF 规范的 PDF（内嵌 CSV 数据）"""
        if not self.items:
            QMessageBox.warning(self, "提示", "当前没有作业数据可导出！")
            return

        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存 UAF 文件", 
            f"ChawPanel作业板_{os.path.basename(self.csv_path).replace('.csv', '')}.uaf.pdf", 
            "UAF.PDF作业文件 (*.uaf.pdf)"
        )
        if not file_path:
            return
        try:
            # 1. 生成 PDF（返回临时文件路径）
            tmp_pdf = self._generate_pdf_with_pdfkit()
            
            # 2. 将 CSV 数据作为附件嵌入
            self._embed_csv_attachment(tmp_pdf, file_path)
            
            # 3. 删除临时文件
            if os.path.exists(tmp_pdf):
                os.remove(tmp_pdf)
            
            QMessageBox.information(self, "导出成功", f"UAF 文件已保存至：\n{file_path}")


        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"发生错误：{e}")



    def _generate_pdf_with_pdfkit(self) -> str:
        """使用 pdfkit 生成 PDF，返回临时文件路径"""
        import pdfkit
        import tempfile
        import os


        wkhtmltopdf_path = os.path.join(os.path.dirname(__file__),"assets","runtime","wkhtmltopdf","bin","wkhtmltopdf.exe")  


        # 确保路径存在
        if not os.path.exists(wkhtmltopdf_path):
            raise FileNotFoundError(f"找不到 wkhtmltopdf：{wkhtmltopdf_path}")

        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # 构建 HTML 字符串
        html_content = self._build_uaf_html()

        # 生成临时文件
        fd, tmp_pdf = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)

        # 转换 HTML 为 PDF
        pdfkit.from_string(html_content, tmp_pdf, configuration=config, options={
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '15mm',
            'margin-right': '15mm',
            'encoding': 'UTF-8',
            'enable-local-file-access': None,
            'disable-smart-shrinking': None,
        })

        return tmp_pdf

    def _build_uaf_html(self) -> str:
        # 生成表格行，每行两列
        rows_html = ""
        items = self.items
        for i in range(0, len(items), 2):
            row_items = items[i:i+2]
            row_html = "<tr>"
            for item in row_items:
                content_lines = item.content.replace('\n', '<br>')
                tags_html = ""
                if item.tags:
                    for tag in item.tags.split(';'):
                        if tag.strip():
                            tags_html += f'<span style="background:#EAF3FC; padding:2px 10px; border-radius:14px; margin-right:4px; color:#0067C0; font-size:9pt; border:1px solid #C7E0F6;">{tag.strip()}</span>'
                # 每个卡片放在一个 td 中
                row_html += f'''
                <td style="width:50%; padding:0 8px 16px 8px; vertical-align:top;">
                    <div style="background:#FFFFFF; border-radius:8px; border:1px solid #E6E6E6; border-left:4px solid #0067C0; padding:12pt 16pt; box-shadow:0 1px 3px rgba(0,0,0,0.06); page-break-inside:avoid; box-sizing:border-box;">
                        <div style="display:table; width:100%; margin-bottom:8pt;">
                            <span style="display:table-cell; color:#1B1B1B; font-size:14pt; font-weight:600;">{item.subject}</span>
                            <span style="display:table-cell; text-align:right; font-size:10pt; color:#606060;">{item.date}</span>
                        </div>
                        <div style="font-size:12pt; line-height:1.6; margin:8pt 0; white-space:pre-wrap; color:#3B3B3B;">{content_lines}</div>
                        <div style="margin-top:6pt;">{tags_html}</div>
                    </div>
                </td>
                '''
            # 如果该行只有一个卡片，补一个空单元格维持两列结构
            if len(row_items) == 1:
                row_html += '<td style="width:50%;"></td>'
            row_html += "</tr>"
            rows_html += row_html

        return f'''
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: A4; margin: 0; }}
            body {{
                background: #fff;
                font-family:"微软雅黑", "Microsoft YaHei", sans-serif;
                padding: 20mm 15mm;
                margin: 0;
                color: #1B1B1B;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }}
            .watermark {{
                color: #1B1B1B;
                opacity: 0.08;
                font-size: 10pt;
                font-weight: 900;
                position: fixed;
                bottom: 30pt;
                right: 30pt;
                transform: rotate(-20deg);
                pointer-events: none;
                z-index: -1;
            }}
        </style>
        </head>
        <body>
            <div class="watermark">使用UAF1.0导出</div>
            <div class="watermark" style="top:10pt; left:10pt; font-size:8pt; opacity:0.06;">
                <small>由 ChawPanel 生成</small>
            </div>
            <table>
                {rows_html}
            </table>
        </body>
        </html>
        '''
    def _embed_csv_attachment(self, input_pdf_path: str, output_pdf_path: str):
        """将 CSV 数据作为附件嵌入到 PDF 中"""
        from pypdf import PdfReader, PdfWriter
        import csv
        import io

        # 1. 准备 CSV 数据
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["subject", "date", "content", "tags"])
        for item in self.items:
            writer.writerow([item.subject, item.date, item.content, item.tags])
        csv_data = csv_buffer.getvalue().encode('utf-8')

        # 2. 读取原 PDF
        reader = PdfReader(input_pdf_path)
        writer_pdf = PdfWriter()
        for page in reader.pages:
            writer_pdf.add_page(page)

        # 3. 添加附件
        writer_pdf.add_attachment("uaf_payload.csv", csv_data)

        # 4. 保存到目标路径
        with open(output_pdf_path, 'wb') as f:
            writer_pdf.write(f)


    def import_uaf(self):
        """从合规的 UAF PDF 中导入数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 UAF 文件", "", 
            "UAF.PDF作业文件 (*.uaf.pdf;*.pdf)"
        )
        if not file_path:
            return

        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            
            # 检查附件中是否有 uaf_payload.csv
            if not reader.attachments:
                QMessageBox.warning(self, "导入失败", "该 PDF 不包含 UAF 数据附件 (uaf_payload.csv)")
                return
            
            csv_data = None
            for name, content in reader.attachments.items():
                if name == "uaf_payload.csv":
                    if isinstance(content, list):
                        csv_data = b''.join(content).decode('utf-8')
                    else:
                        csv_data = content.decode('utf-8')
                        break
            
            if csv_data is None:
                QMessageBox.warning(self, "导入失败", "未找到名为 uaf_payload.csv 的附件")
                return

            # 解析 CSV
            import csv
            import io
            reader_csv = csv.DictReader(io.StringIO(csv_data))
            
            new_items = []
            for row in reader_csv:
                # 验证必填字段
                if not row.get("subject") or not row.get("content"):
                    continue
                new_items.append(DataReader.HomeworkItem(
                    subject=row["subject"],
                    date=row.get("date", datetime.datetime.now().strftime("%Y-%m-%d")),
                    content=row["content"],
                    tags=row.get("tags", "")
                ))

            if not new_items:
                QMessageBox.warning(self, "导入失败", "CSV 文件中没有有效的作业数据")
                return

            # 询问用户是覆盖还是追加
            reply = QMessageBox.question(
                self, "导入选项", 
                f"检测到 {len(new_items)} 条作业数据。\n是否覆盖当前数据？（选“否”则追加到末尾）",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.items = new_items
            else:  # No -> 追加
                # 检查科目重名
                existing_subjects = {item.subject for item in self.items}
                conflict_items = [it for it in new_items if it.subject in existing_subjects]

                if conflict_items:
                    conflict_names = "、".join(it.subject for it in conflict_items)

                    # ---- 用带中文按钮的 QMessageBox 询问处理方式 ----
                    msg = QMessageBox(self)
                    msg.setWindowTitle("科目冲突")
                    msg.setIcon(QMessageBox.Question)
                    msg.setText(f"以下科目在当前数据中已存在：\n\n{conflict_names}")
                    msg.setInformativeText("请选择处理方式：")

                    overwrite_btn = msg.addButton("覆盖", QMessageBox.YesRole)
                    keep_btn = msg.addButton("保留原内容", QMessageBox.NoRole)
                    cancel_btn = msg.addButton("取消导入", QMessageBox.RejectRole)
                    msg.setDefaultButton(keep_btn)   # 默认「保留」更安全
                    msg.exec_()

                    clicked = msg.clickedButton()

                    if clicked is cancel_btn:
                        return
                    elif clicked is overwrite_btn:
                        # 覆盖：先移除原有同名科目
                        conflict_subjects = {it.subject for it in conflict_items}
                        self.items = [it for it in self.items if it.subject not in conflict_subjects]
                        # new_items 保持原样，稍后全部追加
                    else:  # 保留原内容
                        # 从导入数据中剔除冲突科目
                        new_items = [it for it in new_items if it.subject not in existing_subjects]
                        if not new_items:
                            QMessageBox.information(
                                self, "提示",
                                "所有科目均已存在且选择保留原内容，未导入任何数据。"
                            )
                            return

                self.items.extend(new_items)

            # 保存到当前 CSV 并刷新界面
            DataReader.write_homework_to_csv(self.csv_path, self.items)
            self.render_blocks()
            
            QMessageBox.information(self, "导入成功", f"成功导入 {len(new_items)} 条作业数据！")


        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"发生错误：{e}")

class AddBlockWindow(QDialog):  # 添加作业板块窗口
    add_block_signal = Signal(str, str, str)  # subject, content, tags

    def __init__(self):
        super().__init__()
        self.setWindowTitle("添加作业板块")
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.resize(307, 155)
        self.setFixedSize(307, 155)
        self.ui = load_ui("ask_add_what_subject.ui", self)

        self.setLayout(self.ui.layout())

        self.ui.confirm_button.clicked.connect(self.confirm)
        subject_choices = self.ui.subject_choice

        subject_choices.addItems(settings["subjects"])


    def confirm(self):
        subject = self.ui.subject_choice.currentText()


        
        self.add_block_signal.emit(subject, "", "")
        self.close()

    
class ChoosedateWindow(QDialog):  # 添加作业板块窗口
    load_block_signal = Signal(str)  #传入路径： ...\homework_data\yyyy-m-d.csv

    def __init__(self):
        super().__init__()
        self.setWindowTitle("选择日期")
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.resize(515, 315)
        self.setFixedSize(515, 315)
        self.ui = load_ui("choose_date.ui", self)

        self.setLayout(self.ui.layout())

        self.ui.confirm_button.clicked.connect(self.confirm)



    def confirm(self):



        date = self.ui.date_choice.selectedDate().toString("yyyy-M-d")
        self.load_block_signal.emit(os.path.join(os.path.dirname(__file__), "homework_datas", f"{date}.csv"))
        self.close()

class AddTagWindow(QDialog):  # 添加标签窗口
    add_tag_signal = Signal(str)  # tag
    remove_tag_signal = Signal(str)  # tag

    def __init__(self):
        super().__init__()
        self.setWindowTitle("添加标签")
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.resize(324, 170)
        self.setFixedSize(324, 170)
        self.ui = load_ui("add_tag.ui", self)

        self.setLayout(self.ui.layout())

        self.ui.confirm_button.clicked.connect(self.confirm)
        self.ui.del_button.clicked.connect(self.remove_tag)
        tag_choices = self.ui.tag_choice
        tag_choices.addItems(settings["tags"])

    def confirm(self):
        tag = self.ui.tag_choice.currentText()



        self.add_tag_signal.emit(tag)
        self.close()

    def remove_tag(self):
        tag = self.ui.tag_choice.currentText()



        self.remove_tag_signal.emit(tag)
        self.close()


MAIN_WINDOW = MainBoard()

if __name__ == "__main__":

    MAIN_WINDOW.show()
    sys.exit(app.exec_())




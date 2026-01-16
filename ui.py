import streamlit as st
import subprocess
import os
import streamlit.components.v1 as components
import time
import signal

# ตั้งค่าหน้าเว็บ (Layout: Wide)
st.set_page_config(page_title="Confluence to Outline Migrator", page_icon="🚀", layout="wide")

st.title("🚀 Confluence -> Outline Migrator")
st.markdown("เครื่องมือย้ายข้อมูลสำหรับทีม (Self-Service)")

# --- ส่วนที่ 1: Configuration ---
st.header("1. ตั้งค่าการเชื่อมต่อ (Configuration)")

with st.expander("📝 คลิกเพื่อกรอก Key และ Token", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Confluence (Source)")
        conf_url = st.text_input("Confluence URL", value="https://myorder-ecrm.atlassian.net")
        conf_email = st.text_input("Confluence Email")
        conf_token = st.text_input("Confluence API Token", type="password")

    with col2:
        st.subheader("Outline (Destination)")
        outline_domain = st.text_input("Outline Domain", value="https://outline-dev.myorder.dev")
        outline_token = st.text_input("Outline API Token", type="password")
    
    group_options = [
        "claim", "data-analyst", "data-engineer", "data-engineer-lead",
        "devops", "devops.intern", "engineering-manager", "finance",
        "general-manager", "human-resource", "mod-full-stack-developer",
        "mod-full-stack-lead", "mxp-full-stack-developer", "mxp-full-stack-lead",
        "pin-full-stack-developer", "pin-full-stack-lead", "product-owner",
        "sale", "technical-lead", "ui-developer"
    ]
    
    manager_group = st.selectbox(
        "Manager Group (Optional)",
        options=[""] + group_options,
        index=0, 
        help="Group ที่จะให้เป็นคนจัดการ Collection (ถ้าไม่เลือกจะเป็น Private)"
    )

# --- ส่วนที่ 2: URL List ---
st.header("2. รายการลิงก์ที่ต้องการย้าย")
url_list_text = st.text_area("แปะ URL ที่นี่ (บรรทัดละ 1 ลิงก์)", height=200, help="Copy URL จาก Confluence มาแปะได้เลย")

# --- ส่วนที่ 3: ตัวเลือก ---
st.header("3. ตัวเลือก (Options)")
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    skip_setup = st.checkbox("Skip Setup (เร็วขึ้นถ้าเคยรันแล้ว)", value=False)
with col_opt2:
    cleanup = st.checkbox("Cleanup เมื่องานเสร็จ (ลบไฟล์ขยะ)", value=True)

# --- ปุ่มสั่งรัน ---
st.write("---")
# ปุ่ม Start ปุ่มเดียว (Stop ใช้ Browser Control)
if st.button("🚀 Start Migration", type="primary"):
    if not conf_email or not conf_token or not outline_token or not url_list_text:
        st.error("❌ กรุณากรอกข้อมูลให้ครบทุกช่อง")
    else:
        # 1. Config Workspace
        workspace_dir = "workspace"
        os.makedirs(workspace_dir, exist_ok=True)
        
        env_content = f"""
CONFLUENCE_URL={conf_url}
CONFLUENCE_EMAIL={conf_email}
CONFLUENCE_API_TOKEN={conf_token}
OUTLINE_DOMAIN={outline_domain}
OUTLINE_TOKEN={outline_token}
MANAGER_GROUP_NAME={manager_group}
INPUT_FILE=workspace/url_list.txt
OUTPUT_FOLDER=output
CREATOR_REPORT_FILE=creator_report.txt
MIGRATION_ROOT=migrate
MIGRATION_STAGE_DIR=migrate/staging
MIGRATION_ARTIFACT_DIR=migrate/artifacts
"""
        with open(os.path.join(workspace_dir, ".env"), "w", encoding="utf-8") as f:
            f.write(env_content)
        
        with open(os.path.join(workspace_dir, "url_list.txt"), "w", encoding="utf-8") as f:
            f.write(url_list_text.strip())

        # 2. Command
        script_path = "migration.sh" 
        if os.path.exists("workspace/migration.sh"):
             script_path = "workspace/migration.sh"

        cmd = ["bash", script_path]
        if skip_setup: cmd.append("--skip-0") 
        if not cleanup: cmd.append("--skip-9")

        # 3. UI Setup
        status_box = st.empty()
        log_placeholder = st.empty()
        status_box.info("⏳ กำลังทำงาน... (หากต้องการยกเลิก ให้กด Refresh หรือปุ่ม Stop ที่ Browser)")
        
        full_log = ""
        last_update_time = 0
        process = None

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                preexec_fn=os.setsid 
            )
            
            # JS Auto Scroll
            js_scroll = """
            <script>
                var textareas = window.parent.document.querySelectorAll('textarea[aria-label="Console Output"]');
                for (var i = 0; i < textareas.length; i++) {
                    textareas[i].scrollTop = textareas[i].scrollHeight;
                }
            </script>
            """

            # Loop อ่าน Log
            for line in process.stdout:
                full_log += line
                
                # Throttling: อัปเดตทุก 0.1 วิ (Log ขึ้นจอชัวร์ ไม่พัง)
                current_time = time.time()
                if current_time - last_update_time > 0.1:
                    log_placeholder.text_area(
                        label="Console Output",
                        value=full_log,
                        height=500,
                        disabled=True
                    )
                    components.html(js_scroll, height=0)
                    last_update_time = current_time
            
            process.wait()
            
            log_placeholder.text_area(
                label="Console Output",
                value=full_log,
                height=500,
                disabled=True
            )
            components.html(js_scroll, height=0)
            
            if process.returncode == 0:
                status_box.success("✅ การย้ายข้อมูลเสร็จสมบูรณ์!")
                time.sleep(0.5)
                st.toast("การย้ายข้อมูลเสร็จสมบูรณ์! 🎉", icon="✅")
                time.sleep(1)
                st.balloons()
            else:
                status_box.error("❌ เกิดข้อผิดพลาด")
                st.toast("เกิดข้อผิดพลาดในการทำงาน", icon="❌")
                st.error("❌ เกิดข้อผิดพลาด กรุณาดู Log ด้านบน")
                
        except Exception as e:
            st.error(f"Error launching script: {e}")
            
        finally:
            # Logic: ถ้า Script หลุด loop (เช่น user กด Stop/Refresh) ให้ฆ่า Process ทิ้ง
            if process and process.poll() is None:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except:
                    pass
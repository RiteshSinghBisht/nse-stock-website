import xlwings as xw
import os
import logging
import pandas as pd
import time
from config import CHART_PATH, ICON_BULL, ICON_BEAR

def write_to_excel(data, excel_file, is_bearish, sheet_name='Stock_Data'):
    """
    Professional update with LOADING SHEET visible during entire execution.
    - "Loading" sheet stays active (UX feedback)
    - All work happens invisibly behind-the-scenes
    - Instant final reveal to Stock_Data
    """
    app = None
    wb = None
    try:
        HEADER_ROW = 9
        DATA_START_ROW = 10
        PASSWORD = ""
        BACKEND_SHEET = "Dashboard_Backend"
        LOADING_SHEET = "Loading"  # Your loading sheet name
        
        ICON_IMAGE = ICON_BEAR if is_bearish else ICON_BULL
        excel_file = os.path.abspath(excel_file)

        links = []
        if 'Groww_Link' in data.columns:
            links = data['Groww_Link'].tolist()
            display_data = data.drop(columns=['Groww_Link'])
        else:
            display_data = data

        if not os.path.exists(excel_file):
            logging.error(f"Excel file not found at: {excel_file}")
            return

        # --- 1. CONNECT & FULL SILENCE ---
        if len(xw.apps) > 0:
            try:
                wb = xw.books[os.path.basename(excel_file)]
                app = wb.app
            except:
                app = xw.apps.active
                wb = app.books.open(excel_file)
        else:
            app = xw.App(visible=True)
            wb = app.books.open(excel_file)

        # *** TOTAL BLACKOUT MODE ***
        app.api.ScreenUpdating = False
        app.api.DisplayAlerts = False
        app.api.EnableEvents = False
        app.screen_updating = False
        app.display_alerts = False

        # --- 2. ACTIVATE LOADING SHEET FIRST ---
        loading_ws = None
        if LOADING_SHEET in [s.name for s in wb.sheets]:
            loading_ws = wb.sheets[LOADING_SHEET]
            loading_ws.activate()
        # Keep Loading sheet visible to user during entire process

        # --- 3. GET WORK SHEETS ---
        if sheet_name in [s.name for s in wb.sheets]:
            ws_data = wb.sheets[sheet_name]
        else:
            ws_data = wb.sheets.add(sheet_name)
        
        sheet_names = [s.name for s in wb.sheets]
        if BACKEND_SHEET in sheet_names:
            ws_backend = wb.sheets[BACKEND_SHEET]
        else:
            ws_backend = wb.sheets.add(BACKEND_SHEET)

        # --- 4. UNPROTECT SILENTLY ---
        try:
            ws_data.api.Unprotect()
            ws_backend.api.Unprotect()
        except:
            pass

        # --- 5. UPDATE DATA (Loading sheet visible to user) ---
        ws_data.range(f'A{DATA_START_ROW + 1}:M1000').clear_contents()
        if not display_data.empty:
            ws_data.range(f'A{DATA_START_ROW + 1}').options(index=False, header=False).value = display_data

        for i, link in enumerate(links):
            cell = ws_data.range(f'B{DATA_START_ROW + 1 + i}')
            if link:
                cell.add_hyperlink(link, text_to_display=cell.value)

        # --- 6. UPDATE BACKEND IMAGES (Loading still visible) ---
        ws_backend.visible = False
        ws_backend.activate()

        # Clear old pictures
        while len(ws_backend.pictures) > 0:
            try:
                ws_backend.pictures[0].delete()
            except:
                break

        # Add new images (no screen updates)
        if os.path.exists(CHART_PATH):
            ws_backend.pictures.add(CHART_PATH, name='NiftyChart', update=False,
                                  left=ws_backend.range('B2').left, top=ws_backend.range('B2').top)
        if os.path.exists(ICON_IMAGE):
            ws_backend.pictures.add(ICON_IMAGE, name='TrendIcon', update=False,
                                  left=ws_backend.range('K2').left, top=ws_backend.range('K2').top)

        ws_backend.range('O5').value = "Bear Market" if is_bearish else "Bull Market"

        # --- 7. TRIGGER VBA MACRO (All invisible) ---
        try:
            wb.macro("UpdateDashboard_Combined")()
        except Exception as macro_err:
            logging.warning(f"Macro failed (non-critical): {macro_err}")

        # --- 8. PROTECT & SAVE ---
        try:
            ws_data.api.Cells.Locked = True
            ws_data.api.Protect(PASSWORD)
            ws_backend.api.Protect(PASSWORD)
        except:
            pass
        
        wb.save()
        logging.info(f"Dashboard updated. Status: {'Bear' if is_bearish else 'Bull'} Market.")

    except Exception as e:
        logging.error(f"Excel write error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # *** INSTANT REVEAL: Loading → Stock_Data ***
        if app and wb:
            try:
                # Restore Excel state
                app.api.ScreenUpdating = True
                app.api.DisplayAlerts = True
                app.api.EnableEvents = True
                app.screen_updating = True
                app.display_alerts = True
                
                # MAGIC MOMENT: Switch to final result
                ws_data.activate()
                ws_backend.visible = False
                wb.save()
                app.activate()
                
            except Exception as cleanup_err:
                logging.error(f"Final reveal failed: {cleanup_err}")

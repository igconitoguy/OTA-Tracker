import customtkinter as ctk
import threading
import json
import requests
import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
from utils.request import Request

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

class OplusOTAFinder(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("OPLUS OTA Finder")
        self.geometry("800x900")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create header
        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="OPLUS OTA Finder", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.desc_label = ctk.CTkLabel(
            self.main_frame, 
            text="Find and download OTA updates for OPPO, Realme, and OnePlus devices",
            font=ctk.CTkFont(size=14)
        )
        self.desc_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Input section
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        # Product Model
        self.add_input_field(0, "Product Model:", "product_model")
        
        # OTA Version
        self.add_input_field(1, "OTA Version:", "ota_version")
        
        # RUI Version
        rui_options = ["4", "5", "6"]
        self.add_dropdown_field(2, "RUI Version:", "rui_version", rui_options, default="6")
        
        # Region
        region_options = ["GL", "CN", "IN", "EU"]
        self.add_dropdown_field(3, "Region:", "region", region_options, default="GL")
        
        # NV Identifier
        self.add_input_field(4, "NV Identifier:", "nv_identifier")
        
        # GUID
        self.add_input_field(5, "GUID:", "guid", default_value="0")
        
        # IMEI 0
        self.add_input_field(6, "IMEI 0:", "imei0")
        
        # IMEI 1
        self.add_input_field(7, "IMEI 1 (Optional):", "imei1")
        
        # Language
        self.add_input_field(8, "Language:", "language", default_value="en-EN")

        # Checkboxes
        checkbox_frame = ctk.CTkFrame(self.main_frame)
        checkbox_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.beta_var = tk.BooleanVar(value=False)
        self.beta_checkbox = ctk.CTkCheckBox(
            checkbox_frame, text="Beta", variable=self.beta_var
        )
        self.beta_checkbox.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.old_method_var = tk.BooleanVar(value=False)
        self.old_method_checkbox = ctk.CTkCheckBox(
            checkbox_frame, text="Use Old Method", variable=self.old_method_var
        )
        self.old_method_checkbox.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        # Submit button
        self.submit_button = ctk.CTkButton(
            self.main_frame, text="Submit", command=self.on_submit
        )
        self.submit_button.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        # Response section
        self.response_label = ctk.CTkLabel(
            self.main_frame, text="Response:", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.response_label.grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.response_text = ctk.CTkTextbox(self.main_frame, height=150)
        self.response_text.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.response_text.insert("0.0", "OTA information will appear here")
        
        # Results section (initially hidden)
        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        self.results_frame.grid_columnconfigure(0, weight=1)

    def add_input_field(self, row, label_text, name, default_value=""):
        label = ctk.CTkLabel(self.input_frame, text=label_text)
        label.grid(row=row, column=0, padx=(20, 10), pady=10, sticky="w")
        
        entry = ctk.CTkEntry(self.input_frame)
        entry.grid(row=row, column=1, padx=(0, 20), pady=10, sticky="ew")
        entry.insert(0, default_value)
        
        # Add binding to OTA version field to auto-fill product model
        if name == "ota_version":
            entry.bind("<FocusOut>", self.auto_fill_product_model)
        
        setattr(self, f"{name}_entry", entry)

    def auto_fill_product_model(self, event=None):
        """Auto-fill product model based on OTA version"""
        ota_version = self.ota_version_entry.get()
        if ota_version and "_" in ota_version:
            # Extract product model (part before first underscore)
            product_model = ota_version.split("_")[0]
            # Update product model field if it's empty or if auto-fill is needed
            current_model = self.product_model_entry.get()
            if not current_model or current_model != product_model:
                self.product_model_entry.delete(0, "end")
                self.product_model_entry.insert(0, product_model)
                self.update_response_text(f"Product model automatically set to: {product_model}")

    def add_dropdown_field(self, row, label_text, name, options, default=""):
        label = ctk.CTkLabel(self.input_frame, text=label_text)
        label.grid(row=row, column=0, padx=(20, 10), pady=10, sticky="w")
        
        dropdown = ctk.CTkOptionMenu(self.input_frame, values=options)
        dropdown.grid(row=row, column=1, padx=(0, 20), pady=10, sticky="ew")
        if default in options:
            dropdown.set(default)
        else:
            dropdown.set(options[0])
        
        setattr(self, f"{name}_dropdown", dropdown)

    def on_submit(self):
        # Disable submit button and show processing message
        self.submit_button.configure(state="disabled", text="Processing...")
        self.response_text.delete("0.0", "end")
        self.response_text.insert("0.0", "Waiting for response...")
        self.update()
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Create a thread to perform request
        thread = threading.Thread(target=self.perform_request)
        thread.daemon = True
        thread.start()

    def perform_request(self):
        try:
            # Get input values
            model = self.product_model_entry.get()
            ota_version = self.ota_version_entry.get()
            rui_version = int(self.rui_version_dropdown.get())
            region = self.region_dropdown.get()
            nv_identifier = self.nv_identifier_entry.get()
            guid = self.guid_entry.get()
            imei0 = self.imei0_entry.get()
            imei1 = self.imei1_entry.get()
            language = self.language_entry.get()
            beta = self.beta_var.get()
            old_method = self.old_method_var.get()
            
            # Create request
            request = Request(
                req_version=1 if old_method or rui_version == 1 else 2,
                model=model,
                ota_version=ota_version,
                rui_version=rui_version,
                nv_identifier=nv_identifier,
                region=region,
                device_id=guid,
                imei0=imei0,
                imei1=imei1,
                beta=beta,
                language=language
            )
            
            # Set vars and get body/headers
            request.set_vars()
            req_body, req_headers, plain_body = request.set_body_headers()
            
            # Log request info
            print(f"Request URL: {request.url}")
            print(f"Request headers: {json.dumps(req_headers, indent=4)}")
            print(f"Request body: {req_body}")
            
            # Show in UI
            self.update_response_text(f"Sending request to: {request.url}")
            
            # Make the request
            response = requests.post(
                request.url, 
                data=req_body, 
                headers=req_headers,
                timeout=30
            )
            
            # Process response
            self.process_response(response, request, ota_version, model, rui_version, 
                                  nv_identifier, region, guid, imei0, imei1, beta, 
                                  language, old_method)
            
        except Exception as e:
            self.update_response_text(f"Error: {str(e)}")
            self.enable_submit_button()

    def process_response(self, response, request, ota_version, model, rui_version, 
                         nv_identifier, region, guid, imei0, imei1, beta, 
                         language, old_method):
        try:
            # Parse JSON response
            response_json = response.json()
            response_code = response_json.get("responseCode")
            
            # Handle 304 status (no update)
            if response_code == 304:
                if not ota_version.endswith("0000_000000000000"):
                    # Modify OTA version and retry
                    modified_ota = ota_version[:-17] + "0000_000000000000"
                    self.update_response_text(f"Received 304. Retrying with modified OTA version: {modified_ota}")
                    
                    # Update the UI
                    self.ota_version_entry.delete(0, "end")
                    self.ota_version_entry.insert(0, modified_ota)
                    
                    # Create new request with modified version
                    new_request = Request(
                        req_version=1 if old_method or rui_version == 1 else 2,
                        model=model,
                        ota_version=modified_ota,
                        rui_version=rui_version,
                        nv_identifier=nv_identifier,
                        region=region,
                        device_id=guid,
                        imei0=imei0,
                        imei1=imei1,
                        beta=beta,
                        language=language
                    )
                    
                    # Set vars and get body/headers
                    new_request.set_vars()
                    req_body, req_headers, _ = new_request.set_body_headers()
                    
                    # Make a new request
                    new_response = requests.post(
                        new_request.url, 
                        data=req_body, 
                        headers=req_headers,
                        timeout=30
                    )
                    
                    # Process the new response
                    self.process_response(new_response, new_request, modified_ota, model, 
                                         rui_version, nv_identifier, region, guid, 
                                         imei0, imei1, beta, language, old_method)
                    return
                else:
                    self.update_response_text("Error: Received 304 with already modified OTA version.")
                    self.enable_submit_button()
                    return
            
            # Validate response
            request.validate_response(response.status_code, response.text)
            
            # Extract and decrypt body
            body = response_json.get("body", "")
            if body:
                # Decrypt the body
                decrypted_content = request.decrypt(body)
                content = json.loads(decrypted_content)
                
                # Update response text
                self.update_response_text(json.dumps(content, indent=4))
                
                # Process the components
                if "components" in content:
                    self.display_component_info(content)
            else:
                self.update_response_text("No body to decrypt in the response.")
            
        except Exception as e:
            self.update_response_text(f"Error processing response: {str(e)}")
        
        finally:
            self.enable_submit_button()

    def update_response_text(self, text):
        # Update in the main thread
        self.after(0, lambda: self._update_text(text))
    
    def _update_text(self, text):
        self.response_text.delete("0.0", "end")
        self.response_text.insert("0.0", text)
    
    def enable_submit_button(self):
        # Enable in the main thread
        self.after(0, lambda: self.submit_button.configure(state="normal", text="Submit"))

    def display_component_info(self, content):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        components = content.get("components", [])
        if not components:
            return
        
        # Log component information to response text area
        component_log = "OTA Update Details:\n" + "-" * 50 + "\n"
        for idx, component in enumerate(components):
            comp_packets = component.get("componentPackets", {})
            component_log += f"Component #{idx+1}:\n"
            component_log += f"  Version: {component.get('componentVersion', 'N/A')}\n"
            component_log += f"  Size: {comp_packets.get('size', 'N/A')}\n"
            component_log += f"  MD5: {comp_packets.get('md5', 'N/A')}\n"
            component_log += f"  URL: {comp_packets.get('url', 'N/A')}\n"
            component_log += f"  Android Version: {content.get('realAndroidVersion', 'N/A')}\n"
            component_log += f"  OS Version: {content.get('realOsVersion', 'N/A')}\n"
            component_log += "-" * 50 + "\n"
        
        # Update the response text with component details
        self.update_response_text(component_log)
        
        # Title for results
        result_title = ctk.CTkLabel(
            self.results_frame, 
            text="OTA Update Details", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        result_title.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="w")
        
        # Create a component card for each component
        for i, component in enumerate(components):
            self.create_component_card(i+1, component, content)
    
    def create_component_card(self, row, component, content):
        # Create card frame with improved styling
        card = ctk.CTkFrame(self.results_frame, corner_radius=10, border_width=1)
        card.grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        
        # Component name and version with better styling
        header = ctk.CTkLabel(
            card, 
            text=f"OTA Update Details", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        # Extract component packets
        comp_packets = component.get("componentPackets", {})
        
        # Create info frame with better styling
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(2, weight=0)
        
        # Add information in a more organized grid layout
        info_items = [
            ("Version", component.get("componentVersion", "N/A")),
            ("Size", comp_packets.get("size", "N/A")),
            ("MD5", comp_packets.get("md5", "N/A")),
            ("Android Version", content.get("realAndroidVersion", "N/A")),
            ("OS Version", content.get("realOsVersion", "N/A"))
        ]
        
        # Extract security patch info from vabInfo if available
        vab_info = comp_packets.get("vabInfo", {}).get("data", {})
        header_array = vab_info.get("header", [])
        header_map = {}
        
        for header_item in header_array:
            parts = header_item.split("=")
            if len(parts) == 2:
                header_map[parts[0]] = parts[1]
        
        info_items.append(("Security Patch", header_map.get("security_patch", "N/A")))
        
        # Add additional VAB info if available
        for key, value in header_map.items():
            if key != "security_patch":
                info_items.append((key.replace("_", " ").title(), value))
        
        # Create labels and entry fields for each info item with copy buttons
        for idx, (label_text, value_text) in enumerate(info_items):
            # Label with improved styling
            label = ctk.CTkLabel(
                info_frame,
                text=f"{label_text}:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            label.grid(row=idx, column=0, padx=(0, 10), pady=(5, 5), sticky="w")
            
            # Value in an entry widget for easy selection/copying
            value_entry = ctk.CTkEntry(
                info_frame,
                width=400,
                border_width=0,
                fg_color="transparent"
            )
            value_entry.grid(row=idx, column=1, padx=0, pady=(5, 5), sticky="ew")
            value_entry.insert(0, value_text)
            value_entry.configure(state="readonly")
            
            # Copy button for each field
            copy_btn = ctk.CTkButton(
                info_frame,
                text="Copy",
                width=60,
                height=24,
                command=lambda t=value_text: self.copy_to_clipboard(t)
            )
            copy_btn.grid(row=idx, column=2, padx=(5, 0), pady=(5, 5), sticky="e")
        
        # URL for download
        url = comp_packets.get("url", "")
        
        # URL display with horizontal scrolling capability - improved styling
        url_frame = ctk.CTkFrame(card)
        url_frame.grid(row=2, column=0, padx=15, pady=(10, 5), sticky="ew")
        url_frame.grid_columnconfigure(1, weight=1)
        
        url_label = ctk.CTkLabel(
            url_frame,
            text="Download URL:",
            font=ctk.CTkFont(weight="bold")
        )
        url_label.grid(row=0, column=0, padx=(10, 10), pady=(8, 8), sticky="w")
        
        url_entry = ctk.CTkEntry(
            url_frame,
            width=400
        )
        url_entry.grid(row=0, column=1, padx=0, pady=(8, 8), sticky="ew")
        url_entry.insert(0, url)
        url_entry.configure(state="readonly")
        
        # Copy URL button
        url_copy_btn = ctk.CTkButton(
            url_frame,
            text="Copy",
            width=60,
            height=24,
            command=lambda: self.copy_to_clipboard(url)
        )
        url_copy_btn.grid(row=0, column=2, padx=(5, 10), pady=(8, 8), sticky="e")
        
        # Action buttons with improved styling
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=15, pady=(10, 15), sticky="e")
        
        copy_button = ctk.CTkButton(
            button_frame, 
            text="Copy All Details",
            command=lambda: self.copy_all_details(component, content)
        )
        copy_button.grid(row=0, column=0, padx=(0, 10), pady=0)
        
        download_button = ctk.CTkButton(
            button_frame, 
            text="Download",
            command=lambda: self.download_file(url)
        )
        download_button.grid(row=0, column=1, padx=0, pady=0)
        
    def copy_to_clipboard(self, text):
        """Copy text to clipboard and show notification"""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update_response_text("Text copied to clipboard")
        
    def copy_all_details(self, component, content):
        """Copy all component details to clipboard"""
        comp_packets = component.get("componentPackets", {})
        vab_info = comp_packets.get("vabInfo", {}).get("data", {})
        header_array = vab_info.get("header", [])
        header_map = {}
        
        for header_item in header_array:
            parts = header_item.split("=")
            if len(parts) == 2:
                header_map[parts[0]] = parts[1]
        
        details = "OTA Update Details\n"
        details += "=" * 50 + "\n"
        details += f"Version: {component.get('componentVersion', 'N/A')}\n"
        details += f"Size: {comp_packets.get('size', 'N/A')}\n"
        details += f"MD5: {comp_packets.get('md5', 'N/A')}\n"
        details += f"Android Version: {content.get('realAndroidVersion', 'N/A')}\n"
        details += f"OS Version: {content.get('realOsVersion', 'N/A')}\n"
        details += f"Security Patch: {header_map.get('security_patch', 'N/A')}\n"
        
        # Add additional VAB info
        for key, value in header_map.items():
            if key != "security_patch":
                details += f"{key.replace('_', ' ').title()}: {value}\n"
        
        details += f"\nDownload URL: {comp_packets.get('url', '')}\n"
        
        self.copy_to_clipboard(details)

    def download_file(self, url):
        if not url:
            messagebox.showwarning("Download Error", "No URL available for download")
            return
            
        try:
            # Ask for save location
            file_name = url.split('/')[-1]
            save_path = filedialog.asksaveasfilename(
                defaultextension=".zip",
                initialfile=file_name,
                title="Save OTA Update File"
            )
            
            if not save_path:
                return  # User canceled
            
            # Show download progress dialog
            progress_window = ctk.CTkToplevel(self)
            progress_window.title("Downloading")
            progress_window.geometry("400x150")
            progress_window.transient(self)
            progress_window.grab_set()
            
            # Progress label
            progress_label = ctk.CTkLabel(
                progress_window, 
                text=f"Downloading {file_name}...",
                font=ctk.CTkFont(size=16)
            )
            progress_label.pack(pady=(20, 10))
            
            # Progress bar
            progress_bar = ctk.CTkProgressBar(progress_window, width=350)
            progress_bar.pack(pady=10)
            progress_bar.set(0)
            
            # Status label
            status_label = ctk.CTkLabel(
                progress_window, 
                text="Starting download...",
                font=ctk.CTkFont(size=12)
            )
            status_label.pack(pady=5)
            
            # Start download in a thread
            threading.Thread(
                target=self._download_file_thread, 
                args=(url, save_path, progress_window, progress_bar, status_label)
            ).start()
            
        except Exception as e:
            messagebox.showerror("Download Error", f"Error starting download: {str(e)}")

    def _download_file_thread(self, url, save_path, window, progress_bar, status_label):
        try:
            # Make request with stream=True for downloading large files
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                
                # Get file size if available
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Update progress if we know the total size
                            if total_size > 0:
                                progress = downloaded / total_size
                                status_text = f"Downloaded {downloaded/1048576:.1f} MB of {total_size/1048576:.1f} MB"
                                
                                # Update UI in main thread
                                self.after(0, lambda: progress_bar.set(progress))
                                self.after(0, lambda: status_label.configure(text=status_text))
            
            # Download complete
            self.after(0, lambda: window.destroy())
            self.after(0, lambda: messagebox.showinfo("Download Complete", f"File saved to {save_path}"))
            
        except Exception as e:
            self.after(0, lambda: window.destroy())
            self.after(0, lambda: messagebox.showerror("Download Error", f"Error during download: {str(e)}"))

if __name__ == "__main__":
    app = OplusOTAFinder()
    app.mainloop()
from asyncio import protocols
from asyncio import protocols
from PIL import TiffImagePlugin
import os
import glob
from datetime import datetime
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from api.services.hos_engine import DutyStatus, DutySegment


class LogGenerator:

    TEMPLATE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "static",
        "templates",
        "log_template.png"
    )
    MEDIA_LOGS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "media",
        "logs"
    )

    GRID_X0 = 127
    GRID_X1 = 897
    GRID_WIDTH = 770.0  # GRID_X1 - GRID_X0

    ROW_Y_MAP = {
        DutyStatus.OFF_DUTY: 380,
        DutyStatus.SLEEPER_BERTH: 415,
        DutyStatus.DRIVING: 449,
        DutyStatus.ON_DUTY_NOT_DRIVING: 483,
    }

    # @classmethod
    # def get_locs(cls, loc1, loc2):
    #     cls.pickup_locy1 = loc1
    #     cls.dropoff_locy1 = loc2

    # pickup_loc1=None
    # dropoff_loc1=None
    # @classmethod
    # def get_locs(cls,pickup_loc,dropoff_loc):
    #     cls.pickup_loc1=pickup_loc
    #     cls.dropoff_loc1=dropoff_loc
    #     # return pickup_loc,dropoff_loc

    @classmethod
    def get_font(cls, size: int = 14, bold: bool = False):
        """Helper to get a clean TrueType font or fallback default font."""
        font_names = ["arialbd.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf"] if bold else ["arial.ttf", "calibri.ttf", "DejaVuSans.ttf"]
        for fn in font_names:
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                continue
        return ImageFont.load_default()

    @classmethod
    def time_to_x(cls, dt: datetime) -> float:
        """Convert a datetime object (time component) into grid X pixel coordinate."""
        hours_decimal = dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0)
        return cls.GRID_X0 + (hours_decimal / 24.0) * cls.GRID_WIDTH


    # # pickup_loc,dropoff_loc=get_locs(pickup_loc,dropoff_loc)
    # @classmethod
    # def generate_logs(
    #     cls,
    #     daily_buckets: Dict[str, List[DutySegment]],
    #     total_trip_miles: float,
    #     carrier_name: str = "N/A — generated trip plan",
    #     main_office: str = "Washington, D.C.",
    #     home_terminal: str = "Richmond, VA",
    #     truck_number: str = "T-101 / Tr-502",
    #     from_location: str = "",  # <--- Added parameter
    #     to_location: str = "",    # <--- Added parameter
    # ) -> List[Dict[str, Any]]:
    #     """
    #     Generate daily log PNGs for each calendar day bucket.

    #     :param daily_buckets: Dict mapping date string ('YYYY-MM-DD') to list of DutySegments for that day.
    #     :param total_trip_miles: Total miles driven across trip.
    #     :param carrier_name: Motor carrier name.
    #     :param main_office: Carrier main office address.
    #     :param home_terminal: Home terminal address.
    #     :param truck_number: Truck/Tractor vehicle license or numbers.
    #     :return: List of daily log metadata dicts containing day_number, date, png_url, hours summary.
    #     """
    #     os.makedirs(cls.MEDIA_LOGS_DIR, exist_ok=True)
        
    #     # Clear old generated logs
    #     for old_png in glob.glob(os.path.join(cls.MEDIA_LOGS_DIR, "daily_log_day_*.png")):
    #         try:
    #             os.remove(old_png)
    #         except Exception:
    #             pass

    #     if not os.path.exists(cls.TEMPLATE_PATH):
    #         raise FileNotFoundError(f"Canonical log template not found at {cls.TEMPLATE_PATH}")

    #     generated_logs = []
    #     sorted_dates = sorted(daily_buckets.keys())

    #     cum_cycle_running = 0.0

    #     for day_index, date_str in enumerate(sorted_dates, start=1):
    #         segments = daily_buckets[date_str]
    #         date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    #         # Open fresh template copy
    #         template_img = Image.open(cls.TEMPLATE_PATH).convert("RGBA")
    #         draw = ImageDraw.Draw(template_img)

    #         # Colors & Fonts
    #         line_color = (0, 32, 128, 255)  # Navy blue log line
    #         text_color = (0, 0, 0, 255)
    #         line_width = 4

    #         font_sm = cls.get_font(13)
    #         font_md = cls.get_font(16, bold=True)
    #         font_lg = cls.get_font(20, bold=True)

    #         # 1. Fill Header Fields
    #         # Date (Month, Day, Year)
    #         draw.text((365, 15), date_obj.strftime("%m"), fill=text_color, font=font_md)
    #         draw.text((445, 15), date_obj.strftime("%d"), fill=text_color, font=font_md)
    #         draw.text((525, 15), date_obj.strftime("%Y"), fill=text_color, font=font_md)

    #         draw.text((190, 69), from_location, fill=text_color, font=font_md) # Draws From location
    #         draw.text((550, 69), to_location, fill=text_color, font=font_md)   # Draws To location

    #         # Carrier Name & Addresses
    #         draw.text((450, 130), carrier_name, fill=text_color, font=font_md)
    #         # draw.text((450, 150), carrier_name, fill=text_color, font=font_sm)
    #         draw.text((450, 170), main_office, fill=text_color, font=font_md)
    #         # draw.text((450, 190), main_office, fill=text_color, font=font_sm)
    #         draw.text((450, 210), home_terminal, fill=text_color, font=font_md)
    #         # draw.text((450, 230), home_terminal, fill=text_color, font=font_sm)

    #         # Truck/Trailer Numbers
    #         draw.text((205, 210), truck_number, fill=text_color, font=font_md)
    #         # draw.text((185, 205), truck_number, fill=text_color, font=font_sm)

    #         # Calculate daily total hours per row
    #         row_totals = {
    #             DutyStatus.OFF_DUTY: 0.0,
    #             DutyStatus.SLEEPER_BERTH: 0.0,
    #             DutyStatus.DRIVING: 0.0,
    #             DutyStatus.ON_DUTY_NOT_DRIVING: 0.0,
    #         }

    #         # 2. Draw Duty Status Lines & Connectors on Grid
    #         prev_x = None
    #         prev_y = None
    #         remarks_entries = []

    #         for seg in segments:
    #             x_start = cls.time_to_x(seg.start_time)
    #             x_end = cls.time_to_x(seg.end_time)
    #             y_row = cls.ROW_Y_MAP.get(seg.status, cls.ROW_Y_MAP[DutyStatus.OFF_DUTY])

    #             row_totals[seg.status] += seg.duration_hours

    #             # Draw vertical connector from previous status if status changed
    #             if prev_x is not None and prev_y is not None and prev_y != y_row:
    #                 draw.line([(x_start, prev_y), (x_start, y_row)], fill=line_color, width=line_width)

    #             # Draw horizontal status line
    #             draw.line([(x_start, y_row), (x_end, y_row)], fill=line_color, width=line_width)

    #             # Record remark annotation for status changes
    #             if seg.location and (not remarks_entries or remarks_entries[-1][1] != seg.location):
    #                 remarks_entries.append((x_start, seg.location, seg.status))

    #             prev_x = x_end
    #             prev_y = y_row

    #         # Calculate daily miles driven
    #         daily_miles = round(row_totals[DutyStatus.DRIVING] * 60.0, 1)  # approx 60 mph average
    #         draw.text((185, 140), f"{daily_miles:.1f}", fill=text_color, font=font_md)
    #         draw.text((315, 140), f"{daily_miles:.1f}", fill=text_color, font=font_md)

    #         # 3. Write Total Hours Column (Right side of grid X=935)
    #         for status, y_row in cls.ROW_Y_MAP.items():
    #             hrs = row_totals[status]
    #             hrs_str = f"{hrs:.2f}".rstrip("0").rstrip(".") if hrs > 0 else "0"
    #             draw.text((930, y_row - 8), hrs_str, fill=text_color, font=font_md)

    #         total_day_hours = sum(row_totals.values())
    #         draw.text((930, 515), f"={float(total_day_hours):.1f}", fill=text_color, font=font_lg)
    #         # draw.text((930, 515), f"={int(round(total_day_hours))}", fill=text_color, font=font_lg)

    #         # 4. Fill Remarks Section (Y=560..800)
    #         draw.text((130, 535), " Location Annotations:", fill=text_color, font=font_sm)
    #         rem_y = 570
    #         for rem_x, rem_loc, rem_stat in remarks_entries:
    #             if rem_y < 800:
    #                 status_short = rem_stat.replace("_", " ").title()
    #                 # Draw a diagonal or leader line from grid to remarks if helpful, or text label
    #                 draw.text((140, rem_y), f"• {rem_loc} ({status_short})", fill=text_color, font=font_sm)
    #                 rem_y += 22

    #         # 5. 70-Hour Rolling Recap Box (Bottom of template Y=890..960)
    #         day_on_duty = row_totals[DutyStatus.DRIVING] + row_totals[DutyStatus.ON_DUTY_NOT_DRIVING]
    #         cum_cycle_running += day_on_duty
    #         avail_tomorrow = max(0.0, 70.0 - cum_cycle_running)


    #         draw.text((150, 870), f"{float(total_day_hours):.1f} hrs", fill=text_color, font=font_md)
    #         draw.text((316, 870), f"{day_on_duty:.1f} hrs", fill=text_color, font=font_md)
    #         # draw.text((310, 895), f"{day_on_duty:.1f} hrs", fill=text_color, font=font_sm)
    #         draw.text((395, 870), f"{avail_tomorrow:.1f} hrs", fill=text_color, font=font_md)
    #         # draw.text((395, 895), f"{avail_tomorrow:.1f} hrs", fill=text_color, font=font_sm)
    #         draw.text((475, 870), f"{cum_cycle_running:.1f} hrs", fill=text_color, font=font_md)
    #         # draw.text((475, 895), f"{cum_cycle_running:.1f} hrs", fill=text_color, font=font_sm)

    #         # Save PNG output
    #         file_name = f"daily_log_day_{day_index}.png"
    #         output_path = os.path.join(cls.MEDIA_LOGS_DIR, file_name)
    #         template_img.save(output_path, "PNG")

    #         generated_logs.append({
    #             "day_number": day_index,
    #             "date": date_str,
    #             "png_url": f"/media/logs/{file_name}",
    #             "total_driving_hours": round(row_totals[DutyStatus.DRIVING], 2),
    #             "total_on_duty_hours": round(row_totals[DutyStatus.ON_DUTY_NOT_DRIVING], 2),
    #             "total_off_duty_hours": round(row_totals[DutyStatus.OFF_DUTY], 2),
    #             "total_miles_driven": daily_miles,
    #         })

    #     return generated_logs


    @classmethod
    def generate_logs(
        cls,
        daily_buckets: Dict[str, List[DutySegment]],
        total_trip_miles: float,
        carrier_name: str = "N/A — generated trip plan",
        main_office: str = "Washington, D.C.",
        home_terminal: str = "Richmond, VA",
        truck_number: str = "T-101 / Tr-502",
        from_location: str = "",
        to_location: str = "",
    ) -> List[Dict[str, Any]]:
        
        os.makedirs(cls.MEDIA_LOGS_DIR, exist_ok=True)
        
        for old_png in glob.glob(os.path.join(cls.MEDIA_LOGS_DIR, "daily_log_day_*.png")):
            try:
                os.remove(old_png)
            except Exception:
                pass

        if not os.path.exists(cls.TEMPLATE_PATH):
            raise FileNotFoundError(f"Canonical log template not found at {cls.TEMPLATE_PATH}")

        generated_logs = []
        sorted_dates = sorted(daily_buckets.keys())
        cum_cycle_running = 0.0

        for day_index, date_str in enumerate(sorted_dates, start=1):
            segments = daily_buckets[date_str]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            template_img = Image.open(cls.TEMPLATE_PATH).convert("RGBA")
            draw = ImageDraw.Draw(template_img)

            line_color = (0, 32, 128, 255)
            text_color = (0, 0, 0, 255)
            line_width = 4

            font_sm = cls.get_font(13)
            font_md = cls.get_font(16, bold=True)
            font_lg = cls.get_font(20, bold=True)

            # 1. Fill Header Fields
            draw.text((365, 15), date_obj.strftime("%m"), fill=text_color, font=font_md)
            draw.text((445, 15), date_obj.strftime("%d"), fill=text_color, font=font_md)
            draw.text((525, 15), date_obj.strftime("%Y"), fill=text_color, font=font_md)

            # From & To Locations
            draw.text((185, 67), from_location, fill=text_color, font=font_md)
            draw.text((545, 67), to_location, fill=text_color, font=font_md)

            # Carrier Name & Addresses
            draw.text((450, 130), carrier_name, fill=text_color, font=font_md)
            draw.text((450, 170), main_office, fill=text_color, font=font_md)
            draw.text((450, 210), home_terminal, fill=text_color, font=font_md)
            draw.text((205, 210), truck_number, fill=text_color, font=font_md)

            # Calculate Row Totals
            row_totals = {
                DutyStatus.OFF_DUTY: 0.0,
                DutyStatus.SLEEPER_BERTH: 0.0,
                DutyStatus.DRIVING: 0.0,
                DutyStatus.ON_DUTY_NOT_DRIVING: 0.0,
            }

            # 2. Draw Duty Status Lines & Connectors on Grid
            prev_x = None
            prev_y = None
            remarks_entries = []

            for seg in segments:
                x_start = cls.time_to_x(seg.start_time)
                x_end = cls.time_to_x(seg.end_time)
                y_row = cls.ROW_Y_MAP.get(seg.status, cls.ROW_Y_MAP[DutyStatus.OFF_DUTY])

                row_totals[seg.status] += seg.duration_hours

                if prev_x is not None and prev_y is not None and prev_y != y_row:
                    draw.line([(x_start, prev_y), (x_start, y_row)], fill=line_color, width=line_width)

                draw.line([(x_start, y_row), (x_end, y_row)], fill=line_color, width=line_width)

                if seg.location and (not remarks_entries or remarks_entries[-1][1] != seg.location):
                    remarks_entries.append((x_start, seg.location, seg.status))

                prev_x = x_end
                prev_y = y_row

            # 2. Draw Duty Status Lines & Connectors on Grid
            # prev_x = None
            # prev_y = None
            # remarks_entries = []

            # for seg in segments:
            #     x_start = cls.time_to_x(seg.start_time)
            #     x_end = cls.time_to_x(seg.end_time)
            #     y_row = cls.ROW_Y_MAP.get(seg.status, cls.ROW_Y_MAP[DutyStatus.OFF_DUTY])

            #     row_totals[seg.status] += seg.duration_hours

            #     # Draw vertical status change line
            #     if prev_x is not None and prev_y is not None and prev_y != y_row:
            #         draw.line([(x_start, prev_y), (x_start, y_row)], fill=line_color, width=line_width)

            #     # Draw horizontal status duration line
            #     draw.line([(x_start, y_row), (x_end, y_row)], fill=line_color, width=line_width)

            #     if seg.location and (not remarks_entries or remarks_entries[-1][1] != seg.location):
            #         remarks_entries.append((x_start, seg.location, seg.status))

            #     prev_x = x_end
            #     prev_y = y_row

            # Fill to Midnight (24:00) if total status hours < 24
            # total_day_hours = sum(row_totals.values())
            # if total_day_hours < 24.0 and prev_x is not None and prev_y is not None:
            #     padding_hours = 24.0 - total_day_hours
            #     row_totals[DutyStatus.OFF_DUTY] += padding_hours
            #     off_duty_y = cls.ROW_Y_MAP[DutyStatus.OFF_DUTY]
                
            #     # Draw connector up/down to Off Duty row if needed
            #     if prev_y != off_duty_y:
            #         draw.line([(prev_x, prev_y), (prev_x, off_duty_y)], fill=line_color, width=line_width)
                
            #     # Draw remaining line to Midnight
            #     draw.line([(prev_x, off_duty_y), (cls.GRID_X1, off_duty_y)], fill=line_color, width=line_width)
            #     total_day_hours = 24.0

            # Fill to Midnight (24:00) if total status hours < 24
            total_day_hours = sum(row_totals.values())
            if total_day_hours < 24.0 and prev_x is not None and prev_y is not None:
                padding_hours = 24.0 - total_day_hours
                row_totals[DutyStatus.OFF_DUTY] += padding_hours
                off_duty_y = cls.ROW_Y_MAP[DutyStatus.OFF_DUTY]
                
                # 1. Draw VERTICAL connector from last active row (e.g. Driving) up to Off Duty
                if prev_y != off_duty_y:
                    draw.line([(prev_x, prev_y), (prev_x, off_duty_y)], fill=line_color, width=line_width)
                
                # 2. Draw HORIZONTAL line ONLY on Off Duty row to grid end (GRID_X1)
                draw.line([(prev_x, off_duty_y), (cls.GRID_X1, off_duty_y)], fill=line_color, width=line_width)
                
                # Update end coordinates so no extra lines are drawn
                prev_x = cls.GRID_X1
                prev_y = off_duty_y
                total_day_hours = 24.0



            # 3. Daily Miles (Proportional or fallback)
            daily_miles = round(row_totals[DutyStatus.DRIVING] * 60.0, 1)
            draw.text((185, 140), f"{daily_miles:.1f}", fill=text_color, font=font_md)
            draw.text((315, 140), f"{daily_miles:.1f}", fill=text_color, font=font_md)

            # 4. Write Total Hours Column
            for status, y_row in cls.ROW_Y_MAP.items():
                hrs = row_totals[status]
                hrs_str = f"{hrs:.2f}".rstrip("0").rstrip(".") if hrs > 0 else "0"
                draw.text((930, y_row - 8), hrs_str, fill=text_color, font=font_md)

            draw.text((930, 515), f"={float(total_day_hours):.1f}", fill=text_color, font=font_lg)

            # 5. Remarks Section
            draw.text((130, 535), " Location Annotations:", fill=text_color, font=font_sm)
            rem_y = 570
            for rem_x, rem_loc, rem_stat in remarks_entries:
                if rem_y < 800:
                    status_short = rem_stat.replace("_", " ").title()
                    draw.text((140, rem_y), f"• {rem_loc} ({status_short})", fill=text_color, font=font_sm)
                    rem_y += 22

            # 6. Recap Box (FIXED: Uses day_on_duty instead of total_day_hours)
            day_on_duty = row_totals[DutyStatus.DRIVING] + row_totals[DutyStatus.ON_DUTY_NOT_DRIVING]
            cum_cycle_running += day_on_duty
            avail_tomorrow = max(0.0, 70.0 - cum_cycle_running)

            draw.text((150, 870), f"{day_on_duty:.1f} hrs", fill=text_color, font=font_md) # FIXED
            draw.text((316, 870), f"{day_on_duty:.1f} hrs", fill=text_color, font=font_md)
            draw.text((395, 870), f"{avail_tomorrow:.1f} hrs", fill=text_color, font=font_md)
            draw.text((475, 870), f"{cum_cycle_running:.1f} hrs", fill=text_color, font=font_md)

            file_name = f"daily_log_day_{day_index}.png"
            output_path = os.path.join(cls.MEDIA_LOGS_DIR, file_name)
            template_img.save(output_path, "PNG")

            generated_logs.append({
                "day_number": day_index,
                "date": date_str,
                "png_url": f"/media/logs/{file_name}",
                "total_driving_hours": round(row_totals[DutyStatus.DRIVING], 2),
                "total_on_duty_hours": round(row_totals[DutyStatus.ON_DUTY_NOT_DRIVING], 2),
                "total_off_duty_hours": round(row_totals[DutyStatus.OFF_DUTY], 2),
                "total_miles_driven": daily_miles,
            })

        return generated_logs

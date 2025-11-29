"""
Design Wizards Engine - transformer design, cable sizing, PF correction, battery sizing
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class TransformerDesign:
    """Transformer design result"""
    power_rating: float  # VA
    primary_voltage: float
    secondary_voltage: float
    impedance_percentage: float
    efficiency: float
    core_material: str
    primary_turns: int
    secondary_turns: int


@dataclass
class CableSizingResult:
    """Cable sizing result"""
    conductor_size: str
    conductor_area: float  # mm²
    ampacity: float  # Current capacity
    voltage_drop_percentage: float
    material: str  # "copper", "aluminum"


@dataclass
class PFCorrectionDesign:
    """Power factor correction design"""
    target_pf: float
    required_reactive_power: float  # kvar
    capacitor_bank_size: float  # kvar
    capacitor_configuration: str  # "delta", "wye"
    harmonic_filter_needed: bool


@dataclass
class BatterySizingResult:
    """Battery sizing result"""
    total_capacity: float  # Ah
    nominal_voltage: float  # V
    num_modules: int
    charging_time: float  # hours
    discharge_rate: float  # C-rate


class TransformerDesignWizard:
    """Transformer design calculations"""
    
    # Transformer impedance standards (%)
    IMPEDANCE_STANDARDS = {
        "low": 2.0,
        "medium": 5.0,
        "high": 10.0,
    }
    
    # Core material losses (W/kg)
    CORE_LOSSES = {
        "Silicon Steel": 0.8,
        "Amorphous": 0.25,
        "Nickel": 1.5,
    }
    
    @staticmethod
    def design(power: float, v1: float, v2: float, efficiency_target: float = 0.98,
               core_material: str = "Silicon Steel", impedance_level: str = "medium") -> TransformerDesign:
        """
        Design transformer with specified parameters
        
        Args:
            power: Power rating in VA
            v1: Primary voltage in V
            v2: Secondary voltage in V
            efficiency_target: Target efficiency (0-1)
            core_material: Core material type
            impedance_level: Impedance level (low/medium/high)
        
        Returns:
            TransformerDesign object with calculated parameters
        """
        import math
        
        # Calculate turns ratio and turns
        turns_ratio = v1 / v2
        primary_turns = 100  # Reference turns
        secondary_turns = int(primary_turns / turns_ratio)
        
        # Get impedance for level
        impedance_pct = TransformerDesignWizard.IMPEDANCE_STANDARDS.get(
            impedance_level, 5.0
        )
        
        # Estimate core mass and losses
        # Power in watts = power_rating (assuming unity PF)
        power_watts = power
        core_mass = (power_watts / 1000) * 0.15  # Rough estimate: 150g per kW
        core_loss = TransformerDesignWizard.CORE_LOSSES.get(core_material, 0.8)
        total_loss_watts = core_loss * core_mass
        
        # Calculate winding losses (assuming 10% of total loss)
        winding_loss = total_loss_watts * 0.1
        total_loss = total_loss_watts + winding_loss
        
        # Calculate actual efficiency
        actual_efficiency = power_watts / (power_watts + total_loss) if power_watts > 0 else 0
        
        return TransformerDesign(
            power_rating=power,
            primary_voltage=v1,
            secondary_voltage=v2,
            impedance_percentage=impedance_pct,
            efficiency=actual_efficiency,
            core_material=core_material,
            primary_turns=primary_turns,
            secondary_turns=secondary_turns,
        )


class CableSizingWizard:
    """Cable sizing calculations"""
    
    # Ampacity table (mm² -> A) per IEC 60364
    AMPACITY_TABLE = {
        1.0: 10,
        1.5: 13,
        2.5: 20,
        4: 25,
        6: 32,
        10: 50,
        16: 63,
        25: 85,
        35: 110,
        50: 150,
        70: 190,
        95: 245,
        120: 280,
    }
    
    # Resistivity at 20°C (Ω·mm²/m)
    RESISTIVITY = {
        "copper": 0.0175,
        "aluminum": 0.0278,
    }
    
    @staticmethod
    def size_cable(current: float, distance: float, voltage: float, material: str = "copper",
                   max_voltage_drop: float = 5.0) -> CableSizingResult:
        """
        Size cable for given current, distance, and voltage drop limit
        
        Args:
            current: Load current in A
            distance: Cable length in m (one way)
            voltage: System voltage in V
            material: Cable material ("copper" or "aluminum")
            max_voltage_drop: Maximum allowed voltage drop %
        
        Returns:
            CableSizingResult with selected cable size and specifications
        """
        # Find minimum size for current capacity
        min_area = min(
            [area for area, ampacity in CableSizingWizard.AMPACITY_TABLE.items()
             if ampacity >= current],
            default=max(CableSizingWizard.AMPACITY_TABLE.keys())
        )
        
        # Check voltage drop for the minimum area
        resistivity = CableSizingWizard.RESISTIVITY.get(material, 0.0175)
        total_length = distance * 2  # Round trip
        resistance = (resistivity * total_length) / min_area
        voltage_drop_v = current * resistance
        voltage_drop_pct = (voltage_drop_v / voltage) * 100
        
        # If voltage drop exceeds limit, increase cable size
        selected_area = min_area
        while voltage_drop_pct > max_voltage_drop:
            # Find next larger size
            available_sizes = sorted(CableSizingWizard.AMPACITY_TABLE.keys())
            current_idx = available_sizes.index(selected_area)
            if current_idx >= len(available_sizes) - 1:
                break  # Already at max
            selected_area = available_sizes[current_idx + 1]
            
            # Recalculate voltage drop
            resistance = (resistivity * total_length) / selected_area
            voltage_drop_v = current * resistance
            voltage_drop_pct = (voltage_drop_v / voltage) * 100
        
        ampacity = CableSizingWizard.AMPACITY_TABLE[selected_area]
        
        return CableSizingResult(
            conductor_size=f"{selected_area} mm²",
            conductor_area=selected_area,
            ampacity=float(ampacity),
            voltage_drop_percentage=voltage_drop_pct,
            material=material,
        )


class PFCorrectionWizard:
    """Power factor correction design"""
    
    # Standard capacitor ratings (kvar)
    CAPACITOR_RATINGS = [0.5, 1, 2, 2.5, 5, 7.5, 10, 15, 20, 25, 30, 40, 50]
    
    @staticmethod
    def design_correction(real_power: float, current_pf: float, target_pf: float = 0.95,
                         voltage: float = 400, num_steps: Optional[int] = None) -> PFCorrectionDesign:
        """
        Design power factor correction capacitor bank
        
        Args:
            real_power: Real power in W
            current_pf: Current power factor (0-1)
            target_pf: Target power factor
            voltage: System voltage in V
            num_steps: Number of automatic switching steps (None = fixed)
        
        Returns:
            PFCorrectionDesign with capacitor bank specification
        """
        import math
        
        # Validate inputs
        current_pf = max(0.1, min(1.0, current_pf))
        target_pf = max(0.1, min(1.0, target_pf))
        
        if current_pf >= target_pf:
            # Already at or better than target
            return PFCorrectionDesign(
                target_pf=target_pf,
                required_reactive_power=0.0,
                capacitor_bank_size=0.0,
                capacitor_configuration="delta",
                harmonic_filter_needed=False,
            )
        
        # Calculate reactive power needed
        current_angle = math.acos(current_pf)
        target_angle = math.acos(target_pf)
        
        current_reactive = real_power * math.tan(current_angle)
        target_reactive = real_power * math.tan(target_angle)
        required_reactive = current_reactive - target_reactive
        required_reactive_kvar = required_reactive / 1000
        
        # Select appropriate capacitor bank size (round up to standard rating)
        bank_size = next(
            (rating for rating in PFCorrectionWizard.CAPACITOR_RATINGS
             if rating >= required_reactive_kvar),
            PFCorrectionWizard.CAPACITOR_RATINGS[-1]
        )
        
        # Determine configuration (delta or wye based on voltage)
        config = "delta" if voltage > 230 else "wye"
        
        # Check if harmonic filter needed (if PF was very low)
        harmonic_filter = current_pf < 0.6
        
        return PFCorrectionDesign(
            target_pf=target_pf,
            required_reactive_power=required_reactive_kvar,
            capacitor_bank_size=bank_size,
            capacitor_configuration=config,
            harmonic_filter_needed=harmonic_filter,
        )


class BatterySizingWizard:
    """Battery sizing calculations"""
    
    # Battery specifications per technology
    BATTERY_SPECS = {
        "lithium": {
            "nominal_voltage": 3.7,  # V per cell
            "energy_density": 250,    # Wh/kg
            "cycle_life": 3000,
            "efficiency": 0.95,
            "cost_per_kwh": 150,      # $/kWh
        },
        "lead-acid": {
            "nominal_voltage": 2.0,   # V per cell
            "energy_density": 40,     # Wh/kg
            "cycle_life": 500,
            "efficiency": 0.80,
            "cost_per_kwh": 100,
        },
        "nickel-metal": {
            "nominal_voltage": 1.2,   # V per cell
            "energy_density": 80,     # Wh/kg
            "cycle_life": 1000,
            "efficiency": 0.85,
            "cost_per_kwh": 120,
        },
    }
    
    @staticmethod
    def size_battery(load_power: float, runtime: float, nominal_voltage: float = 48,
                    discharge_rate: float = 0.2, technology: str = "lithium",
                    depth_of_discharge: float = 0.8) -> BatterySizingResult:
        """
        Size battery system with specified parameters
        
        Args:
            load_power: Load power in W
            runtime: Backup runtime in hours
            nominal_voltage: System voltage in V (default 48V)
            discharge_rate: C-rate for discharge (0-1)
            technology: Battery technology type
            depth_of_discharge: Usable capacity fraction (0-1)
        
        Returns:
            BatterySizingResult with calculated battery specifications
        """
        # Calculate energy required (Wh)
        energy_required_wh = load_power * runtime
        
        # Get efficiency for technology
        efficiency = BatterySizingWizard.BATTERY_SPECS.get(
            technology, BatterySizingWizard.BATTERY_SPECS["lithium"]
        )["efficiency"]
        
        # Account for efficiency losses and depth of discharge
        usable_capacity_wh = energy_required_wh / (efficiency * depth_of_discharge)
        
        # Calculate Ah (Amp-hours)
        capacity_ah = usable_capacity_wh / nominal_voltage if nominal_voltage > 0 else 0
        
        # Determine number of modules (standard module = 100 Ah)
        module_capacity = 100  # Ah per module
        num_modules = int(capacity_ah / module_capacity) + (1 if capacity_ah % module_capacity > 0 else 0)
        
        # Recalculate actual total capacity with modules
        total_capacity_ah = num_modules * module_capacity
        
        # Calculate charging time (assuming charge rate = 0.5 * discharge_rate)
        charge_current = discharge_rate * total_capacity_ah
        charging_time = total_capacity_ah / max(charge_current, 0.1)  # hours
        
        return BatterySizingResult(
            total_capacity=total_capacity_ah,
            nominal_voltage=nominal_voltage,
            num_modules=num_modules,
            charging_time=charging_time,
            discharge_rate=discharge_rate,
        )

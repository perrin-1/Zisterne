#!/usr/bin/python
# -*- coding: utf-8 -*- 
 
 
import spidev
import time
import os
import sys
import math
 
# General Definitions
# min dig value 115 (0cm) @4mA @0.6V
# max dig value 614 (500cm) @20mA @5V
# Korrekturfaktor dig value -> Höhe = 26/3 ~ 8.66666667
# Formel: dig - 115 * 78/9

# ================================
# new definition (3V Vref)
# min dig value 204,8 (0cm) @4mA @0.6V
# max dig value 1024 (500cm) @20mA @3V
# Korrekturfaktor dig value -> Höhe = (500/819,2)*(82/84)
# Formel: dig - 204,8 * (500/819,2)*(82/84)
# neuer korr faktor 03-2017 53/71 

h_cf = 53 / 71

#
# Cylinder: Durchmesser 254 cm, Länge 400cm
cyl_radius = 254 / 2
cyl_length = 400
#cyl_length = 336


# number of samples to take per measurement
num_samples = 30 
 
 
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  data = 0
  for x in range(0, num_samples):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data += (float)(((adc[1]&3) << 8) + adc[2]) / (num_samples)
    time.sleep (0.051)
  
  return data
 
# Function to calculate the filled volume of a lying cylinder 
def FillCylinder(radius, fillheight, length):
    Volume = math.pi * radius * radius * length * 1000
    #Convert Volume in Liter
    Volume = Volume / 1000 / 1000

    if (fillheight > (radius * 2)):
        fillheight = radius * 2
        #print (" Warn: Fillheigth > max. Fillheigth ")

    FillVolume = radius * radius * length * (math.acos( (radius - fillheight) / radius ) - (radius - fillheight) * ( math.sqrt( 2 * radius * fillheight - fillheight * fillheight ) / (radius * radius))) * 1000

    #Convert Fillvolume in Liter
    FillVolume = FillVolume / 1000 / 1000

    VolumePercent = FillVolume / Volume * 100

    #print(" The total Volume of a Cylinder = %.5f" %Volume)
    #print(" The Fillvolume of a Cylinder = %.5f" %FillVolume)
    #print(" Fillvolume in %% %.5f" %VolumePercent)
    return FillVolume 

# Function to calculate the volume of a  cylinder 
def VolCylinder(radius, length):
    Volume = math.pi * radius * radius * length * 1000
    #Convert Volume in Liter
    Volume = Volume / 1000 / 1000
    return Volume
 
 
def WaterHeight(value):
    #print ("Digital Value %.3f" %value)
    return ((value-204.8) * 53 / 71)      
#    return (value-204.8) 
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
  volts = (data * 3.0) / float(1023)
  volts = round(volts,places)
  return volts
 

cs = 0
channel = 0

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,cs)

value=ReadChannel(channel)
if (value == 0):
  print "-1;0;0"
else:
  print "%.5f;%5f;%.5f" % (WaterHeight(value), FillCylinder(cyl_radius, WaterHeight(value), cyl_length), VolCylinder(cyl_radius, cyl_length)) 

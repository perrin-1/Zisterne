#!/usr/bin/python
# -*- coding: utf-8 -*- 
 
 
import spidev
import time
import os
import sys
import math
 
# General Definitions
# min dig value 115 (0cm) @4mA @0.6V
# max dig value 614 (500cm) @20mA @3V
# Korrekturfaktor dig value -> Höhe = 26/3 ~ 8.66666667
# Formel: dig - 115 * 78/9
#
# Cylinder: Durchmesser 254 cm, Länge 400cm
cyl_radius = 254 / 2
cyl_length = 400


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
        print (" Warn: Fillheigth > max. Fillheigth ")

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
    return ((value-204.8) #
* 10/(26/3)*614/1024)

# * 25625 / 43008)  
 
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
  volts = (data * 5.0) / float(1023)
  volts = round(volts,places)
  return volts
 
# print "args: " + str(sys.argv)
# Argumente pruefen

if(( sys.argv[1] == '0') or (sys.argv[1] == '1')):
  cs = int(sys.argv[1])
  print "CS: " + str(cs)
else:
  print "Invalid Chip Select Value!"
  sys.exit(1)
    
if((sys.argv[2] >= '0') and (sys.argv[2]<'8')):
  channel = int(sys.argv[2])
  print "Kanal: " + str(channel)
  # Open SPI bus
  spi = spidev.SpiDev()
  spi.open(0,cs)
else:
   print "Invalid Channel!"
   sys.exit(1)


count = 0
while True:
      count += 1
      print "Step " + str(count)
      value=ReadChannel(channel)
      if (value != 0):
        print "Read OK"
      else:
        print "Sondenfehler"
      print 'Hoehe: %.2f' % WaterHeight(value)
      print "Dig: "+str(value)
      print "Fuellmenge %.3f" % FillCylinder(cyl_radius, WaterHeight(value), cyl_length)
      print "Max Fuellmenge %.3f " % VolCylinder(cyl_radius, cyl_length)
      print "Fuellmenge %% %.3f " % (FillCylinder(cyl_radius, WaterHeight(value), cyl_length) / VolCylinder(cyl_radius, cyl_length) * 100)
      print "====================" 
      time.sleep(0.5) 
      

// Static fallback for /api/samples — keeps "Load example" and the sample chips working even
// when the backend is cold-starting or unreachable. Mirrors cpc_classifier/api.py _SAMPLES.
import type { Sample } from "./types";

export const FALLBACK_SAMPLES: Sample[] = [
  {
    label: "RSA public-key cryptosystem — US 4,405,829",
    text:
      "A cryptographic communications system in which a message is encoded as a number M " +
      "and enciphered by raising M to a predetermined power and computing the remainder " +
      "when divided by the product of two predetermined prime numbers; the ciphertext is " +
      "deciphered at the receiving terminal by raising it to a second predetermined power " +
      "associated with the receiver and computing the residue modulo the same product of " +
      "primes, recovering the original message.",
    tag: "Real patent · granted 1983 · expired",
  },
  {
    label: "Wearable blood-glucose sensor",
    text: "A wearable sensor that continuously measures blood glucose and streams readings to a phone.",
    tag: null,
  },
  {
    label: "Neural-network image recognition",
    text: "A method for training a deep neural network to recognise objects in camera images.",
    tag: null,
  },
  {
    label: "Autonomous-car lidar control",
    text: "A system that lets an autonomous car steer itself and adjust speed using lidar and radar.",
    tag: null,
  },
  {
    label: "Secure wireless payment protocol",
    text: "A protocol for secure payment authentication using cryptographic signatures over a wireless network.",
    tag: null,
  },
];

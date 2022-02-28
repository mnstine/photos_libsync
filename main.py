import mediaget
import mediasend

in_source = "Mic project"
out_source = "Mic project"
mediaget.main(in_source)
mediasend.main(out_source)
print('Sync Complete')

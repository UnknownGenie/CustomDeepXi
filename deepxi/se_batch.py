## AUTHOR:         Aaron Nicolson
## AFFILIATION:    Signal Processing Laboratory, Griffith University.
##
## This Source Code Form is subject to the terms of the Mozilla Public
## License, v. 2.0. If a copy of the MPL was not distributed with this
## file, You can obtain one at http://mozilla.org/MPL/2.0/.

import contextlib, glob, os, pickle, platform, random, sys, wave
import numpy as np
from deepxi.utils import read_wav
from scipy.io.wavfile import read

def Batch_list(file_dir, list_name, data_path=None, make_new=False):
	from soundfile import SoundFile, SEEK_END
	'''
	Places the file paths and wav lengths of an audio file into a dictionary, which 
	is then appended to a list. SPHERE format cannot be used. 'glob' is used to 
	support Unix style pathname pattern expansions. Checks if the training list 
	has already been pickled, and loads it. If a different dataset is to be 
	used, delete the pickle file.

	Inputs:
		file_dir - directory containing the wavs.
		list_name - name for the list.
		data_path - path to store pickle files.
		make_new - re-create list.

	Outputs:
		batch_list - list of file paths and wav length.
	'''
	file_name = ['*.wav', '*.flac', '*.mp3']
	if data_path == None: data_path = 'data'
	if not make_new:
		if os.path.exists(data_path + '/' + list_name + '_list_' + platform.node() + '.p'):
			print('Loading ' + list_name + ' list from pickle file...')
			with open(data_path + '/' + list_name + '_list_' + platform.node() + '.p', 'rb') as f:
				batch_list = pickle.load(f)
			if batch_list[0]['file_path'].find(file_dir) != -1: 
				print('The ' + list_name + ' list has a total of %i entries.' % (len(batch_list)))
				return batch_list
	print('Creating ' + list_name + ' list, as no pickle file exists...')
	batch_list = [] # list for wav paths and lengths.
	for fn in file_name:
		for file_path in glob.glob(os.path.join(file_dir, fn)):
			f = SoundFile(file_path)
			seq_len = f.seek(0, SEEK_END)
			batch_list.append({'file_path': file_path, 'seq_len': seq_len}) # append dictionary.
	if not os.path.exists(data_path): os.makedirs(data_path) # make directory.
	with open(data_path + '/' + list_name + '_list_' + platform.node() + '.p', 'wb') as f: 		
		pickle.dump(batch_list, f)
	print('The ' + list_name + ' list has a total of %i entries.' % (len(batch_list)))
	return batch_list

def Batch(fdir, snr_l=[]):
	'''
	REQUIRES REWRITING.

	Places all of the test waveforms from the list into a numpy array. 
	SPHERE format cannot be used. 'glob' is used to support Unix style pathname 
	pattern expansions. Waveforms are padded to the maximum waveform length. The 
	waveform lengths are recorded so that the correct lengths can be sliced 
	for feature extraction. The SNR levels of each test file are placed into a
	numpy array. Also returns a list of the file names.

	Inputs:
		fdir - directory containing the waveforms.
		fnames - filename/s of the waveforms.
		snr_l - list of the SNR levels used.

	Outputs:
		wav_np - matrix of paded waveforms stored as a numpy array.
		len_np - length of each waveform strored as a numpy array.
		snr_test_np - numpy array of all the SNR levels for the test set.
		fname_l - list of filenames.
	'''
	fname_l = [] # list of file names.
	wav_l = [] # list for waveforms.
	snr_test_l = [] # list of SNR levels for the test set.
	# if isinstance(fnames, str): fnames = [fnames] # if string, put into list.
	fnames = ['*.wav', '*.flac', '*.mp3']
	for fname in fnames:
		for fpath in glob.glob(os.path.join(fdir, fname)):
			for snr in snr_l:
				if fpath.find('_' + str(snr) + 'dB') != -1:
					snr_test_l.append(snr) # append SNR level.	
			(wav, _) = read_wav(fpath) # read waveform from given file path.
			if np.isnan(wav).any() or np.isinf(wav).any():
				raise ValueError('Error: NaN or Inf value. File path: %s.' % (file_path))
			wav_l.append(wav) # append.
			fname_l.append(os.path.basename(os.path.splitext(fpath)[0])) # append name.
	len_l = [] # list of the waveform lengths.
	maxlen = max(len(wav) for wav in wav_l) # maximum length of waveforms.
	wav_np = np.zeros([len(wav_l), maxlen], np.int16) # numpy array for waveform matrix.
	for (i, wav) in zip(range(len(wav_l)), wav_l):
		wav_np[i,:len(wav)] = wav # add waveform to numpy array.
		len_l.append(len(wav)) # append length of waveform to list.
	return wav_np, np.array(len_l, np.int32), np.array(snr_test_l, np.int32), fname_l

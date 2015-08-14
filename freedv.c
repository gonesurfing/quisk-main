#include <Python.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>	// Use native C99 complex type for fftw3
#include <sys/types.h>

#include "quisk.h"

int DEBUG;

typedef struct {	// from comp.h
  float real;
  float imag;
} COMP;
// from freedv_api.h
#define FREEDV_MODE_1600        0
#define FREEDV_MODE_700         1
struct freedv;
typedef void (*freedv_callback_rx)(void *, char);
typedef char (*freedv_callback_tx)(void *);

#ifdef MS_WINDOWS
#include <windows.h>
HMODULE WINAPI hLib;
#define GET_HANDLE1			hLib = LoadLibrary(".\\freedvpkg\\libcodec2.dll")
#define GET_HANDLE2			hLib = LoadLibrary(".\\freedvpkg\\libcodec2_32.dll")
#define GET_HANDLE3			hLib = LoadLibrary(".\\freedvpkg\\libcodec2_64.dll")
#define GET_HANDLE4			hLib = LoadLibrary("libcodec2.dll")
#define GET_ADDR(name)		(void *)GetProcAddress(hLib, name)
#define CLOSE_LIB			FreeLibrary(hLib)
#else
#include <dlfcn.h>
void * hLib;
#define GET_HANDLE1			hLib = dlopen("./freedvpkg/libcodec2.so", RTLD_LAZY)
#define GET_HANDLE2			hLib = dlopen("./freedvpkg/libcodec2_32.so", RTLD_LAZY)
#define GET_HANDLE3			hLib = dlopen("./freedvpkg/libcodec2_64.so", RTLD_LAZY)
#define GET_HANDLE4			hLib = dlopen("libcodec2.so", RTLD_LAZY)
#define GET_ADDR(name)		dlsym(hLib,  name)
#define CLOSE_LIB			dlclose(hLib)
#endif

static int quisk_freedv_mode;
static struct freedv * hFdv;
short * speech_out;
float * rxdata;
short * mod_out;
short * speech_in;
static int freedv_version = -1;
// freedv_version is the library version number, or
//   -1		no library was found
//   -2		a library was found, but freedv_get_version is missing

// FreeDV API functions:
// open, close
struct freedv * (*freedv_open)(int mode);
void (*freedv_close)(struct freedv *freedv);
// Transmit
void (*freedv_tx)(struct freedv *freedv, short mod_out[], short speech_in[]);
void (*freedv_comptx)(struct freedv *freedv, COMP mod_out[], short speech_in[]);
// Receive
int (*freedv_nin)(struct freedv *freedv);
int (*freedv_rx)(struct freedv *freedv, short speech_out[], short demod_in[]);
int (*freedv_floatrx)(struct freedv *freedv, short speech_out[], float demod_in[]);
int (*freedv_comprx)(struct freedv *freedv, short speech_out[], COMP demod_in[]);
// Set parameters
void (*freedv_set_callback_txt)(struct freedv *freedv, freedv_callback_rx rx, freedv_callback_tx tx, void *callback_state);
void (*freedv_set_test_frames)			(struct freedv *freedv, int test_frames);
void (*freedv_set_smooth_symbols)		(struct freedv *freedv, int smooth_symbols);
void (*freedv_set_squelch_en)			(struct freedv *freedv, int squelch_en);
void (*freedv_set_snr_squelch_thresh)	(struct freedv *freedv, float snr_squelch_thresh);
// Get parameters
int (*freedv_get_version)(void);
void (*freedv_get_modem_stats)(struct freedv *freedv, int *sync, float *snr_est);
int (*freedv_get_test_frames)			(struct freedv *freedv);
int (*freedv_get_n_speech_samples)		(struct freedv *freedv);
int (*freedv_get_n_max_modem_samples)	(struct freedv *freedv);
int (*freedv_get_n_nom_modem_samples)	(struct freedv *freedv);
int (*freedv_get_total_bits)			(struct freedv *freedv);
int (*freedv_get_total_bit_errors)		(struct freedv *freedv);

static void GetAddrs(void)
{
	if (DEBUG) printf("Try handle 1\n");
	GET_HANDLE1;
	if (hLib) {		// check the first library name
		freedv_version = -2;
		freedv_get_version = GET_ADDR("freedv_get_version");
		if (freedv_get_version != NULL)
			freedv_version = freedv_get_version();
	}
	if (freedv_version < 10) {		// try the next library
		if (hLib)
			CLOSE_LIB;
		if (DEBUG) printf("Try handle 2\n");
		GET_HANDLE2;
		if (hLib) {
			freedv_version = -2;
			freedv_get_version = GET_ADDR("freedv_get_version");
			if (freedv_get_version != NULL)
				freedv_version = freedv_get_version();
		}
	}
	if (freedv_version < 10) {		// try the next library
		if (hLib)
			CLOSE_LIB;
		if (DEBUG) printf("Try handle 3\n");
		GET_HANDLE3;
		if (hLib) {
			freedv_version = -2;
			freedv_get_version = GET_ADDR("freedv_get_version");
			if (freedv_get_version != NULL)
				freedv_version = freedv_get_version();
		}
	}
	if (freedv_version < 10) {		// try the next library
		if (hLib)
			CLOSE_LIB;
		if (DEBUG) printf("Try handle 4\n");
		GET_HANDLE4;
		if (hLib) {
			freedv_version = -2;
			freedv_get_version = GET_ADDR("freedv_get_version");
			if (freedv_get_version != NULL)
				freedv_version = freedv_get_version();
		}
	}
	if (DEBUG) printf("freedv_version is %d\n", freedv_version);
	if (freedv_version < 10) {
		if (hLib)
			CLOSE_LIB;
		return;
	}

// open, close
	freedv_open = GET_ADDR("freedv_open");
	freedv_close = GET_ADDR("freedv_close");
// Transmit
	freedv_tx = GET_ADDR("freedv_tx");
	freedv_comptx = GET_ADDR("freedv_comptx");
// Receive
	freedv_nin = GET_ADDR("freedv_nin");
	freedv_rx = GET_ADDR("freedv_rx");
	freedv_floatrx = GET_ADDR("freedv_floatrx");
	freedv_comprx = GET_ADDR("freedv_comprx");
// Set parameters
	freedv_set_callback_txt = GET_ADDR("freedv_set_callback_txt");
	freedv_set_test_frames = GET_ADDR("freedv_set_test_frames");
	freedv_set_smooth_symbols = GET_ADDR("freedv_set_smooth_symbols");
	freedv_set_squelch_en = GET_ADDR("freedv_set_squelch_en");
	freedv_set_snr_squelch_thresh = GET_ADDR("freedv_set_snr_squelch_thresh");
// Get parameters
	freedv_get_modem_stats = GET_ADDR("freedv_get_modem_stats");
	freedv_get_test_frames = GET_ADDR("freedv_get_test_frames");
	freedv_get_n_speech_samples = GET_ADDR("freedv_get_n_speech_samples");
	freedv_get_n_max_modem_samples = GET_ADDR("freedv_get_n_max_modem_samples");
	freedv_get_n_nom_modem_samples = GET_ADDR("freedv_get_n_nom_modem_samples");
	freedv_get_total_bits = GET_ADDR("freedv_get_total_bits");
	freedv_get_total_bit_errors = GET_ADDR("freedv_get_total_bit_errors");
	return;
}

static int quisk_freedv_rx(double * dsamples, int count)	// Called from the sound thread.
{	// Input digital modulation is dsamples; decoded voice is dsamples
	int i, j, nout, need, have;
	static float * fsamples = NULL;
	static int rxdata_index = 0, fsamples_size=0;
	double scale = (double)CLIP32 / CLIP16;	// convert 32 bits to 16 bits

	if ( ! hFdv)
		return count;

	// check size of fsamples[] buffer
	if (count > fsamples_size) {
		fsamples_size = count * 2;
		if (fsamples)
			free(fsamples);
		fsamples = (float *)malloc(fsamples_size * sizeof(float));
	}
	// copy dsamples to fsamples[]
	for (i = 0; i < count; i++)
		fsamples[i] = (float)dsamples[i];

	nout = 0;
	need = freedv_nin(hFdv);
	//if (rxdata_index >= need)
	//	printf("FreeDV Rx Fault need %d rxdata_index %d count %d\n", need, rxdata_index, count);
	for (i = 0; i < count; i++) {
		rxdata[rxdata_index++] = fsamples[i] / scale;
		if (rxdata_index >= need) {
			have = freedv_floatrx(hFdv, speech_out, rxdata);
			for (j = 0; j < have; j++)
				dsamples[nout++] = speech_out[j] * scale * 0.7;
			rxdata_index = 0;
			need = freedv_nin(hFdv);
		}
	}
	return nout;
}

static int quisk_freedv_tx(double * dsamples, int count)	// Called from the sound thread.
{	// Input voice samples are dsamples; output digital modulation is dsamples.
	int i, j, nout;
	int n_speech_samples;
	static short * ssamples = NULL;
	static int speech_index = 0, speech_size = 0;

	if ( ! hFdv)
		return count;
	// check size of ssamples[] buffer
	if (count > speech_size) {
		speech_size = count * 2;
		if (ssamples)
			free(ssamples);
		ssamples = (short *)malloc(speech_size * sizeof(short));
	}
	// copy dsamples to ssamples[]
	for (i = 0; i < count; i++)
		ssamples[i] = (short)dsamples[i];
	n_speech_samples = freedv_get_n_speech_samples(hFdv);
	nout = 0;
	for (i = 0; i < count; i++) {
		speech_in[speech_index++] = ssamples[i];
		if (speech_index >= n_speech_samples) {
			freedv_tx(hFdv, mod_out, speech_in);
			speech_index = 0;
			for (j = 0; j < n_speech_samples; j++)
				dsamples[nout++] = (double)mod_out[j];
		}
	}
	return nout;
}

#define TX_MSG_SIZE		80
static char quisk_tx_msg[TX_MSG_SIZE];

static char get_next_tx_char(void * callback_state)
{
	char c;
	static int index = 0;

	c = quisk_tx_msg[index++];
	if (index >= TX_MSG_SIZE)
		index = 0;
	if ( ! c) {
		index = 0;
		c = quisk_tx_msg[index++];
	}
	return c;
}

PyObject * quisk_freedv_set_options(PyObject * self, PyObject * args, PyObject * keywds)	// Called from the GUI thread.
{  // Call with keyword arguments ONLY to change parameters.  Call before quisk_freedv_open().
	char * ptMsg=NULL;
	static char * kwlist[] = {"mode", "tx_msg", "DEBUG", NULL} ;

	if (!PyArg_ParseTupleAndKeywords (args, keywds, "|isi", kwlist, &quisk_freedv_mode, &ptMsg, &DEBUG))
		return NULL;
	if (ptMsg)
		strncpy(quisk_tx_msg, ptMsg, TX_MSG_SIZE);
	if (DEBUG) printf("freedv_set_options mode %d tx_msg %s DEBUG %d\n", quisk_freedv_mode, quisk_tx_msg, DEBUG);
	return PyInt_FromLong(1);
}

PyObject * quisk_freedv_open(PyObject * self, PyObject * args)	// Called from the GUI thread.
{
	if (!PyArg_ParseTuple (args, ""))
		return NULL;
	if ( ! hLib)
		GetAddrs();		// Get the entry points for funtions in the codec2 library
	if (DEBUG) printf("freedv_open: version %d\n", freedv_version);
	if (freedv_version < 10)
		return PyInt_FromLong(0);
	hFdv = freedv_open(quisk_freedv_mode);
	if (hFdv == NULL)
		return PyInt_FromLong(0);
	quisk_dvoice_freedv(&quisk_freedv_rx, &quisk_freedv_tx);
	if (quisk_tx_msg[0])
		freedv_set_callback_txt(hFdv, NULL, &get_next_tx_char, NULL);
	freedv_set_squelch_en(hFdv, 1);
	speech_out = (short*)malloc(sizeof(short) * freedv_get_n_speech_samples(hFdv));
	rxdata = (float*)malloc(sizeof(float) * freedv_get_n_max_modem_samples(hFdv));
	mod_out = (short*)malloc(sizeof(short) * freedv_get_n_nom_modem_samples(hFdv));
	speech_in = (short*)malloc(sizeof(short) * freedv_get_n_speech_samples(hFdv));
	return PyInt_FromLong(1);
}

PyObject * quisk_freedv_close(PyObject * self, PyObject * args)
{
	if (!PyArg_ParseTuple (args, ""))
		return NULL;
	if (hFdv) {
		freedv_close(hFdv);
		hFdv = NULL;
		if (hLib)
			CLOSE_LIB;
		hLib = NULL;
		free(speech_out);
		free(rxdata);
		free(mod_out);
		free(speech_in);
		speech_out = mod_out = speech_in = NULL;
		rxdata = NULL;
	}
	Py_INCREF (Py_None);
	return Py_None;
}

PyObject * quisk_freedv_get_snr(PyObject * self, PyObject * args)	// Called from the GUI thread.
{
	float snr_est = 0.0;

	if (!PyArg_ParseTuple (args, ""))
		return NULL;
	if (hFdv)
		freedv_get_modem_stats(hFdv, NULL, &snr_est);
	return PyFloat_FromDouble(snr_est);
}

PyObject * quisk_freedv_get_version(PyObject * self, PyObject * args)	// Called from the GUI thread.
{
	if (!PyArg_ParseTuple (args, ""))
		return NULL;
	if ( ! hLib)
		GetAddrs();		// Get the entry points for funtions in the codec2 library
	return PyInt_FromLong(freedv_version);
}

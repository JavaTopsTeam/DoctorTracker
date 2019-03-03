from django.shortcuts import render,HttpResponseRedirect,reverse
from .models import *
from random import randint
from .utils import *


# Create your views here.

def LoginPage(request):
    return render(request,"doctorfinder/login.html")

def RegistrationPage(request):
    return render(request,'doctorfinder/registration.html')

def forgotPage(request):
    return render(request,"doctorfinder/forgot-password.html")

def Homepage(request):
    if 'email' in request.session and 'role' in request.session:
        if request.session['role'] == 'patient':

            all_doctors = Doctor.objects.all()
            return render(request,'doctorfinder/homepage-patient.html',{'all_doctors':all_doctors})
    else:
        return HttpResponseRedirect(reverse('login'))

def RegisterUser(request):
    try:
        if request.POST['role'] == 'doctor':
            role = request.POST['role']
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            password = request.POST['password']
            confirmpassword = request.POST['confirmpassword']
            gender = request.POST['gender']
            email = request.POST['email']
            speciality = request.POST['speciality']
            dateofbirth = request.POST['birthdate']
            city = request.POST['city']
            mobile = str(request.POST['phone'])

            user = User.objects.filter(email = email)
            if user:
                message = 'This email already exists'
                return render(request,'doctorfinder/registration.html',{'message':message})
            else:
                if password == confirmpassword:
                    otp = randint(100000, 9999999)
                    newuser = User.objects.create(email = email, password= password,role = role, otp = otp)  
                    newdoctor = Doctor.objects.create(user_id = newuser,firstname = firstname, lastname = lastname, gender = gender, speciality = speciality, city = city, mobile = mobile, birthdate = dateofbirth)
                    email_subject = "Doctor Finder : Account Vericication"
                    sendmail(email_subject,'mail_template',email,{'name':firstname,'otp':otp,'link':'http://localhost:8000/enterprise/user_verify/'})
                    return render(request,'doctorfinder/SuccessfulRegistration.html')
                else:
                    message = "Password and confirm password doesn't match"
                    return render(request,'doctorfinder/registration.html',{'message':message})

        else:
            role = request.POST['role']
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            password = request.POST['password']
            confirmpassword = request.POST['confirm']
            gender = request.POST['gender']
            email = request.POST['email']
            dateofbirth = request.POST['birthdate']
            city = request.POST['city']
            mobile = str(request.POST['phone'])
            user = User.objects.filter(email = email)
            if user:
                message = 'This email already exists'
                return render(request,'doctorfinder/registration.html',{'message':message})
            else:
                if password == confirmpassword:
                    otp = randint(100000, 9999999)
                    newuser = User.objects.create(email = email, password= password,role = role, otp = otp)  
                    newpatient = Patient.objects.create(user_id = newuser,firstname = firstname, lastname = lastname, gender = gender, city = city, mobile = mobile, birthdate = dateofbirth)
                    email_subject = "Doctor Finder : Account Vericication"
                    sendmail(email_subject,'mail_template',email,{'name':firstname,'otp':otp,'link':'http://localhost:8000/enterprise/user_verify/'})
                    return render(request,'doctorfinder/SuccessfulRegistration.html')
                else:
                    message = "Password and confirm password doesn't match"
                    return render(request,'doctorfinder/registration.html',{'message':message})
    except User.DoesNotExist:
        message = 'This email already exists'
        return render(request,'doctorfinder/registration.html',{'message':message})

def login_evaluation(request):

    if request.POST['role'] == 'doctor':
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.filter(email = email)
        print(user)
        if user[0]:
            if user[0].password == password and user[0].role == 'doctor':
                doctor = Doctor.objects.filter(user_id = user[0])
                request.session['email'] = user[0].email
                request.session['firstname'] = doctor[0].firstname
                request.session['role'] = user[0].role
                return render(request,"doctorfinder/homepage-doctor.html")
            else:
                message = "Your password is incorrect or user doesn't exist"
                return render(request,"doctorfinder/login.html",{'message':message})
        else:
            message = "user doesn't exist"
            return render(request,"doctorfinder/login.html",{'message':message})

    if request.POST['role'] == 'patient':

        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.filter(email = email)
        print(user)
        if user[0]:
            if user[0].password == password and user[0].role == 'patient':
                patient = Patient.objects.filter(user_id = user[0])
                request.session['email'] = user[0].email
                request.session['firstname'] = patient[0].firstname
                request.session['role'] = user[0].role
                return HttpResponseRedirect(reverse('homepage'))
            else:
                message = "Your password is incorrect or user doesn't exist"
                return render(request,"doctorfinder/login.html",{'message':message})
        else:
            message = "user doesn't exist"
            return render(request,"doctorfinder/login.html",{'message':message})




def forgotPassword(request):
    email = request.POST['email']
    try:
        user = User.objects.get(email = email)
        if user:
            if user.email == email:
                otp = randint(100000, 9999999)
                user.otp=otp
                user.save()
                email_subject = "This is your new OTP"
                sendmail(email_subject,'mail_template',email,{'otp':otp})
                return render(request,'doctorfinder/forgot-password-verification.html',{'email':email})
            else:
                message = 'This email does not match'
                return render(request,"doctorfinder/forgot-password.html",{'message':message})
        else:
            message = 'This email is not available'
            return render(request,"doctorfinder/forgot-password.html",{'message':message})
    except:
        message = 'This email is not available'
        return render(request,"doctorfinder/forgot-password.html",{'message':message})

def logout(request):
    del request.session['email']
    del request.session['role']
    del request.session['firstname']
    return HttpResponseRedirect(reverse('login'))

def ResetPassword(request):
    
    otp = request.POST['otp']
    newPassword = request.POST['newpass']
    confirmPassword = request.POST['confirmpass']
    email = request.POST['email']
    try:
        user = User.objects.get(email = email)
        if confirmPassword == newPassword and str(user.otp) == otp:
            user.password = newPassword
            user.save()
            return HttpResponseRedirect(reverse('login'))
        else:
            message = "Either password and confirm password doesn't match or you have entered a wrong otp"
            return render(request,"doctorfinder/forgot-password-verification.html",{'message':message})
    except:
        message = "Ivalid request"
        return render(request,"doctorfinder/forgot-password-verification.html",{'message':message})


        
